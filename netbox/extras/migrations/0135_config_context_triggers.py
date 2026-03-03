from django.db import migrations


FORWARD_SQL = """
-- =============================================================================
-- 1. jsonb_deepmerge(jsonb, jsonb) - recursive deep merge
-- =============================================================================
CREATE OR REPLACE FUNCTION jsonb_deepmerge(original jsonb, new_data jsonb) RETURNS jsonb AS $$
DECLARE
    result jsonb := original;
    key text;
    new_val jsonb;
    orig_val jsonb;
BEGIN
    IF original IS NULL THEN RETURN new_data; END IF;
    IF new_data IS NULL THEN RETURN original; END IF;

    FOR key, new_val IN SELECT * FROM jsonb_each(new_data)
    LOOP
        orig_val := result -> key;
        IF orig_val IS NOT NULL
           AND jsonb_typeof(orig_val) = 'object' AND orig_val != '{}'::jsonb
           AND jsonb_typeof(new_val) = 'object' AND new_val != '{}'::jsonb
        THEN
            result := jsonb_set(result, ARRAY[key], jsonb_deepmerge(orig_val, new_val));
        ELSE
            result := jsonb_set(result, ARRAY[key], new_val);
        END IF;
    END LOOP;
    RETURN result;
END;
$$ LANGUAGE plpgsql IMMUTABLE;


-- =============================================================================
-- 2. compute_config_context_for_device(bigint) RETURNS jsonb
-- =============================================================================
CREATE OR REPLACE FUNCTION compute_config_context_for_device(device_pk bigint) RETURNS jsonb AS $$
DECLARE
    -- Device attributes
    _site_id bigint;
    _location_id bigint;
    _role_id bigint;
    _platform_id bigint;
    _cluster_id bigint;
    _tenant_id bigint;
    _device_type_id bigint;
    _local_context_data jsonb;
    -- Site FK attributes
    _site_region_id bigint;
    _site_group_id bigint;
    -- Region MPTT
    _region_tree_id integer;
    _region_level integer;
    _region_lft integer;
    _region_rght integer;
    -- SiteGroup MPTT
    _sitegroup_tree_id integer;
    _sitegroup_level integer;
    _sitegroup_lft integer;
    _sitegroup_rght integer;
    -- Role MPTT
    _role_tree_id integer;
    _role_level integer;
    _role_lft integer;
    _role_rght integer;
    -- Platform MPTT
    _platform_tree_id integer;
    _platform_level integer;
    _platform_lft integer;
    _platform_rght integer;
    -- Location MPTT
    _location_tree_id integer;
    _location_level integer;
    _location_lft integer;
    _location_rght integer;
    -- Cluster attributes
    _cluster_type_id bigint;
    _cluster_group_id bigint;
    -- Tenant attributes
    _tenant_group_id bigint;
    -- Tag IDs
    _tag_ids integer[];
    -- Loop/result
    ctx record;
    result jsonb := '{}'::jsonb;
BEGIN
    -- Fetch device attributes
    SELECT site_id, location_id, role_id, platform_id, cluster_id, tenant_id,
           device_type_id, local_context_data
    INTO _site_id, _location_id, _role_id, _platform_id, _cluster_id, _tenant_id,
         _device_type_id, _local_context_data
    FROM dcim_device WHERE id = device_pk;

    IF NOT FOUND THEN RETURN NULL; END IF;

    -- Fetch site's region and group
    SELECT region_id, group_id INTO _site_region_id, _site_group_id
    FROM dcim_site WHERE id = _site_id;

    -- Fetch region MPTT fields
    IF _site_region_id IS NOT NULL THEN
        SELECT tree_id, level, lft, rght
        INTO _region_tree_id, _region_level, _region_lft, _region_rght
        FROM dcim_region WHERE id = _site_region_id;
    END IF;

    -- Fetch site group MPTT fields
    IF _site_group_id IS NOT NULL THEN
        SELECT tree_id, level, lft, rght
        INTO _sitegroup_tree_id, _sitegroup_level, _sitegroup_lft, _sitegroup_rght
        FROM dcim_sitegroup WHERE id = _site_group_id;
    END IF;

    -- Fetch role MPTT fields
    IF _role_id IS NOT NULL THEN
        SELECT tree_id, level, lft, rght
        INTO _role_tree_id, _role_level, _role_lft, _role_rght
        FROM dcim_devicerole WHERE id = _role_id;
    END IF;

    -- Fetch platform MPTT fields
    IF _platform_id IS NOT NULL THEN
        SELECT tree_id, level, lft, rght
        INTO _platform_tree_id, _platform_level, _platform_lft, _platform_rght
        FROM dcim_platform WHERE id = _platform_id;
    END IF;

    -- Fetch location MPTT fields
    IF _location_id IS NOT NULL THEN
        SELECT tree_id, level, lft, rght
        INTO _location_tree_id, _location_level, _location_lft, _location_rght
        FROM dcim_location WHERE id = _location_id;
    END IF;

    -- Fetch cluster type and group
    IF _cluster_id IS NOT NULL THEN
        SELECT type_id, group_id INTO _cluster_type_id, _cluster_group_id
        FROM virtualization_cluster WHERE id = _cluster_id;
    END IF;

    -- Fetch tenant group
    IF _tenant_id IS NOT NULL THEN
        SELECT group_id INTO _tenant_group_id
        FROM tenancy_tenant WHERE id = _tenant_id;
    END IF;

    -- Fetch device's tag IDs
    SELECT array_agg(tag_id) INTO _tag_ids
    FROM extras_taggeditem
    WHERE object_id = device_pk
      AND content_type_id = (
          SELECT id FROM django_content_type
          WHERE app_label = 'dcim' AND model = 'device'
      );

    -- Find all matching active ConfigContexts, ordered by weight, name
    FOR ctx IN
        SELECT cc.data
        FROM extras_configcontext cc
        WHERE cc.is_active = TRUE
          -- regions
          AND (
              NOT EXISTS (SELECT 1 FROM extras_configcontext_regions WHERE configcontext_id = cc.id)
              OR (_site_region_id IS NOT NULL AND EXISTS (
                  SELECT 1 FROM extras_configcontext_regions ecr
                  JOIN dcim_region r ON r.id = ecr.region_id
                  WHERE ecr.configcontext_id = cc.id
                    AND r.tree_id = _region_tree_id
                    AND r.level <= _region_level
                    AND r.lft <= _region_lft
                    AND r.rght >= _region_rght
              ))
          )
          -- site_groups
          AND (
              NOT EXISTS (SELECT 1 FROM extras_configcontext_site_groups WHERE configcontext_id = cc.id)
              OR (_site_group_id IS NOT NULL AND EXISTS (
                  SELECT 1 FROM extras_configcontext_site_groups ecsg
                  JOIN dcim_sitegroup sg ON sg.id = ecsg.sitegroup_id
                  WHERE ecsg.configcontext_id = cc.id
                    AND sg.tree_id = _sitegroup_tree_id
                    AND sg.level <= _sitegroup_level
                    AND sg.lft <= _sitegroup_lft
                    AND sg.rght >= _sitegroup_rght
              ))
          )
          -- sites
          AND (
              NOT EXISTS (SELECT 1 FROM extras_configcontext_sites WHERE configcontext_id = cc.id)
              OR EXISTS (
                  SELECT 1 FROM extras_configcontext_sites
                  WHERE configcontext_id = cc.id AND site_id = _site_id
              )
          )
          -- locations
          AND (
              NOT EXISTS (SELECT 1 FROM extras_configcontext_locations WHERE configcontext_id = cc.id)
              OR (_location_id IS NOT NULL AND EXISTS (
                  SELECT 1 FROM extras_configcontext_locations ecl
                  JOIN dcim_location loc ON loc.id = ecl.location_id
                  WHERE ecl.configcontext_id = cc.id
                    AND loc.tree_id = _location_tree_id
                    AND loc.level <= _location_level
                    AND loc.lft <= _location_lft
                    AND loc.rght >= _location_rght
              ))
          )
          -- device_types
          AND (
              NOT EXISTS (SELECT 1 FROM extras_configcontext_device_types WHERE configcontext_id = cc.id)
              OR EXISTS (
                  SELECT 1 FROM extras_configcontext_device_types
                  WHERE configcontext_id = cc.id AND devicetype_id = _device_type_id
              )
          )
          -- roles
          AND (
              NOT EXISTS (SELECT 1 FROM extras_configcontext_roles WHERE configcontext_id = cc.id)
              OR (_role_id IS NOT NULL AND EXISTS (
                  SELECT 1 FROM extras_configcontext_roles ecr
                  JOIN dcim_devicerole dr ON dr.id = ecr.devicerole_id
                  WHERE ecr.configcontext_id = cc.id
                    AND dr.tree_id = _role_tree_id
                    AND dr.level <= _role_level
                    AND dr.lft <= _role_lft
                    AND dr.rght >= _role_rght
              ))
          )
          -- platforms
          AND (
              NOT EXISTS (SELECT 1 FROM extras_configcontext_platforms WHERE configcontext_id = cc.id)
              OR (_platform_id IS NOT NULL AND EXISTS (
                  SELECT 1 FROM extras_configcontext_platforms ecp
                  JOIN dcim_platform p ON p.id = ecp.platform_id
                  WHERE ecp.configcontext_id = cc.id
                    AND p.tree_id = _platform_tree_id
                    AND p.level <= _platform_level
                    AND p.lft <= _platform_lft
                    AND p.rght >= _platform_rght
              ))
          )
          -- cluster_types
          AND (
              NOT EXISTS (SELECT 1 FROM extras_configcontext_cluster_types WHERE configcontext_id = cc.id)
              OR (_cluster_id IS NOT NULL AND EXISTS (
                  SELECT 1 FROM extras_configcontext_cluster_types
                  WHERE configcontext_id = cc.id AND clustertype_id = _cluster_type_id
              ))
          )
          -- cluster_groups
          AND (
              NOT EXISTS (SELECT 1 FROM extras_configcontext_cluster_groups WHERE configcontext_id = cc.id)
              OR (_cluster_id IS NOT NULL AND _cluster_group_id IS NOT NULL AND EXISTS (
                  SELECT 1 FROM extras_configcontext_cluster_groups
                  WHERE configcontext_id = cc.id AND clustergroup_id = _cluster_group_id
              ))
          )
          -- clusters
          AND (
              NOT EXISTS (SELECT 1 FROM extras_configcontext_clusters WHERE configcontext_id = cc.id)
              OR (_cluster_id IS NOT NULL AND EXISTS (
                  SELECT 1 FROM extras_configcontext_clusters
                  WHERE configcontext_id = cc.id AND cluster_id = _cluster_id
              ))
          )
          -- tenant_groups
          AND (
              NOT EXISTS (SELECT 1 FROM extras_configcontext_tenant_groups WHERE configcontext_id = cc.id)
              OR (_tenant_id IS NOT NULL AND _tenant_group_id IS NOT NULL AND EXISTS (
                  SELECT 1 FROM extras_configcontext_tenant_groups
                  WHERE configcontext_id = cc.id AND tenantgroup_id = _tenant_group_id
              ))
          )
          -- tenants
          AND (
              NOT EXISTS (SELECT 1 FROM extras_configcontext_tenants WHERE configcontext_id = cc.id)
              OR (_tenant_id IS NOT NULL AND EXISTS (
                  SELECT 1 FROM extras_configcontext_tenants
                  WHERE configcontext_id = cc.id AND tenant_id = _tenant_id
              ))
          )
          -- tags
          AND (
              NOT EXISTS (SELECT 1 FROM extras_configcontext_tags WHERE configcontext_id = cc.id)
              OR (_tag_ids IS NOT NULL AND EXISTS (
                  SELECT 1 FROM extras_configcontext_tags
                  WHERE configcontext_id = cc.id AND tag_id = ANY(_tag_ids)
              ))
          )
        ORDER BY cc.weight, cc.name
    LOOP
        result := jsonb_deepmerge(result, ctx.data);
    END LOOP;

    -- Merge local_context_data last (highest priority)
    IF _local_context_data IS NOT NULL AND _local_context_data != 'null'::jsonb THEN
        result := jsonb_deepmerge(result, _local_context_data);
    END IF;

    RETURN result;
END;
$$ LANGUAGE plpgsql STABLE;


-- =============================================================================
-- 3. compute_config_context_for_vm(bigint) RETURNS jsonb
-- =============================================================================
CREATE OR REPLACE FUNCTION compute_config_context_for_vm(vm_pk bigint) RETURNS jsonb AS $$
DECLARE
    -- VM attributes
    _site_id bigint;
    _role_id bigint;
    _platform_id bigint;
    _cluster_id bigint;
    _tenant_id bigint;
    _local_context_data jsonb;
    -- Site FK attributes
    _site_region_id bigint;
    _site_group_id bigint;
    -- Region MPTT
    _region_tree_id integer;
    _region_level integer;
    _region_lft integer;
    _region_rght integer;
    -- SiteGroup MPTT
    _sitegroup_tree_id integer;
    _sitegroup_level integer;
    _sitegroup_lft integer;
    _sitegroup_rght integer;
    -- Role MPTT
    _role_tree_id integer;
    _role_level integer;
    _role_lft integer;
    _role_rght integer;
    -- Platform MPTT
    _platform_tree_id integer;
    _platform_level integer;
    _platform_lft integer;
    _platform_rght integer;
    -- Cluster attributes
    _cluster_type_id bigint;
    _cluster_group_id bigint;
    -- Tenant attributes
    _tenant_group_id bigint;
    -- Tag IDs
    _tag_ids integer[];
    -- Loop/result
    ctx record;
    result jsonb := '{}'::jsonb;
BEGIN
    -- Fetch VM attributes
    SELECT site_id, role_id, platform_id, cluster_id, tenant_id, local_context_data
    INTO _site_id, _role_id, _platform_id, _cluster_id, _tenant_id, _local_context_data
    FROM virtualization_virtualmachine WHERE id = vm_pk;

    IF NOT FOUND THEN RETURN NULL; END IF;

    -- Fetch site's region and group
    IF _site_id IS NOT NULL THEN
        SELECT region_id, group_id INTO _site_region_id, _site_group_id
        FROM dcim_site WHERE id = _site_id;
    END IF;

    -- Fetch region MPTT fields
    IF _site_region_id IS NOT NULL THEN
        SELECT tree_id, level, lft, rght
        INTO _region_tree_id, _region_level, _region_lft, _region_rght
        FROM dcim_region WHERE id = _site_region_id;
    END IF;

    -- Fetch site group MPTT fields
    IF _site_group_id IS NOT NULL THEN
        SELECT tree_id, level, lft, rght
        INTO _sitegroup_tree_id, _sitegroup_level, _sitegroup_lft, _sitegroup_rght
        FROM dcim_sitegroup WHERE id = _site_group_id;
    END IF;

    -- Fetch role MPTT fields
    IF _role_id IS NOT NULL THEN
        SELECT tree_id, level, lft, rght
        INTO _role_tree_id, _role_level, _role_lft, _role_rght
        FROM dcim_devicerole WHERE id = _role_id;
    END IF;

    -- Fetch platform MPTT fields
    IF _platform_id IS NOT NULL THEN
        SELECT tree_id, level, lft, rght
        INTO _platform_tree_id, _platform_level, _platform_lft, _platform_rght
        FROM dcim_platform WHERE id = _platform_id;
    END IF;

    -- Fetch cluster type and group
    IF _cluster_id IS NOT NULL THEN
        SELECT type_id, group_id INTO _cluster_type_id, _cluster_group_id
        FROM virtualization_cluster WHERE id = _cluster_id;
    END IF;

    -- Fetch tenant group
    IF _tenant_id IS NOT NULL THEN
        SELECT group_id INTO _tenant_group_id
        FROM tenancy_tenant WHERE id = _tenant_id;
    END IF;

    -- Fetch VM's tag IDs
    SELECT array_agg(tag_id) INTO _tag_ids
    FROM extras_taggeditem
    WHERE object_id = vm_pk
      AND content_type_id = (
          SELECT id FROM django_content_type
          WHERE app_label = 'virtualization' AND model = 'virtualmachine'
      );

    -- Find all matching active ConfigContexts, ordered by weight, name
    FOR ctx IN
        SELECT cc.data
        FROM extras_configcontext cc
        WHERE cc.is_active = TRUE
          -- regions
          AND (
              NOT EXISTS (SELECT 1 FROM extras_configcontext_regions WHERE configcontext_id = cc.id)
              OR (_site_region_id IS NOT NULL AND EXISTS (
                  SELECT 1 FROM extras_configcontext_regions ecr
                  JOIN dcim_region r ON r.id = ecr.region_id
                  WHERE ecr.configcontext_id = cc.id
                    AND r.tree_id = _region_tree_id
                    AND r.level <= _region_level
                    AND r.lft <= _region_lft
                    AND r.rght >= _region_rght
              ))
          )
          -- site_groups
          AND (
              NOT EXISTS (SELECT 1 FROM extras_configcontext_site_groups WHERE configcontext_id = cc.id)
              OR (_site_group_id IS NOT NULL AND EXISTS (
                  SELECT 1 FROM extras_configcontext_site_groups ecsg
                  JOIN dcim_sitegroup sg ON sg.id = ecsg.sitegroup_id
                  WHERE ecsg.configcontext_id = cc.id
                    AND sg.tree_id = _sitegroup_tree_id
                    AND sg.level <= _sitegroup_level
                    AND sg.lft <= _sitegroup_lft
                    AND sg.rght >= _sitegroup_rght
              ))
          )
          -- sites
          AND (
              NOT EXISTS (SELECT 1 FROM extras_configcontext_sites WHERE configcontext_id = cc.id)
              OR (_site_id IS NOT NULL AND EXISTS (
                  SELECT 1 FROM extras_configcontext_sites
                  WHERE configcontext_id = cc.id AND site_id = _site_id
              ))
          )
          -- locations: VMs never match location-scoped contexts
          AND NOT EXISTS (SELECT 1 FROM extras_configcontext_locations WHERE configcontext_id = cc.id)
          -- device_types: VMs never match device-type-scoped contexts
          AND NOT EXISTS (SELECT 1 FROM extras_configcontext_device_types WHERE configcontext_id = cc.id)
          -- roles
          AND (
              NOT EXISTS (SELECT 1 FROM extras_configcontext_roles WHERE configcontext_id = cc.id)
              OR (_role_id IS NOT NULL AND EXISTS (
                  SELECT 1 FROM extras_configcontext_roles ecr
                  JOIN dcim_devicerole dr ON dr.id = ecr.devicerole_id
                  WHERE ecr.configcontext_id = cc.id
                    AND dr.tree_id = _role_tree_id
                    AND dr.level <= _role_level
                    AND dr.lft <= _role_lft
                    AND dr.rght >= _role_rght
              ))
          )
          -- platforms
          AND (
              NOT EXISTS (SELECT 1 FROM extras_configcontext_platforms WHERE configcontext_id = cc.id)
              OR (_platform_id IS NOT NULL AND EXISTS (
                  SELECT 1 FROM extras_configcontext_platforms ecp
                  JOIN dcim_platform p ON p.id = ecp.platform_id
                  WHERE ecp.configcontext_id = cc.id
                    AND p.tree_id = _platform_tree_id
                    AND p.level <= _platform_level
                    AND p.lft <= _platform_lft
                    AND p.rght >= _platform_rght
              ))
          )
          -- cluster_types
          AND (
              NOT EXISTS (SELECT 1 FROM extras_configcontext_cluster_types WHERE configcontext_id = cc.id)
              OR (_cluster_id IS NOT NULL AND EXISTS (
                  SELECT 1 FROM extras_configcontext_cluster_types
                  WHERE configcontext_id = cc.id AND clustertype_id = _cluster_type_id
              ))
          )
          -- cluster_groups
          AND (
              NOT EXISTS (SELECT 1 FROM extras_configcontext_cluster_groups WHERE configcontext_id = cc.id)
              OR (_cluster_id IS NOT NULL AND _cluster_group_id IS NOT NULL AND EXISTS (
                  SELECT 1 FROM extras_configcontext_cluster_groups
                  WHERE configcontext_id = cc.id AND clustergroup_id = _cluster_group_id
              ))
          )
          -- clusters
          AND (
              NOT EXISTS (SELECT 1 FROM extras_configcontext_clusters WHERE configcontext_id = cc.id)
              OR (_cluster_id IS NOT NULL AND EXISTS (
                  SELECT 1 FROM extras_configcontext_clusters
                  WHERE configcontext_id = cc.id AND cluster_id = _cluster_id
              ))
          )
          -- tenant_groups
          AND (
              NOT EXISTS (SELECT 1 FROM extras_configcontext_tenant_groups WHERE configcontext_id = cc.id)
              OR (_tenant_id IS NOT NULL AND _tenant_group_id IS NOT NULL AND EXISTS (
                  SELECT 1 FROM extras_configcontext_tenant_groups
                  WHERE configcontext_id = cc.id AND tenantgroup_id = _tenant_group_id
              ))
          )
          -- tenants
          AND (
              NOT EXISTS (SELECT 1 FROM extras_configcontext_tenants WHERE configcontext_id = cc.id)
              OR (_tenant_id IS NOT NULL AND EXISTS (
                  SELECT 1 FROM extras_configcontext_tenants
                  WHERE configcontext_id = cc.id AND tenant_id = _tenant_id
              ))
          )
          -- tags
          AND (
              NOT EXISTS (SELECT 1 FROM extras_configcontext_tags WHERE configcontext_id = cc.id)
              OR (_tag_ids IS NOT NULL AND EXISTS (
                  SELECT 1 FROM extras_configcontext_tags
                  WHERE configcontext_id = cc.id AND tag_id = ANY(_tag_ids)
              ))
          )
        ORDER BY cc.weight, cc.name
    LOOP
        result := jsonb_deepmerge(result, ctx.data);
    END LOOP;

    -- Merge local_context_data last (highest priority)
    IF _local_context_data IS NOT NULL AND _local_context_data != 'null'::jsonb THEN
        result := jsonb_deepmerge(result, _local_context_data);
    END IF;

    RETURN result;
END;
$$ LANGUAGE plpgsql STABLE;


-- =============================================================================
-- 4. Helper wrappers: refresh_device_config_context / refresh_vm_config_context
-- =============================================================================
CREATE OR REPLACE FUNCTION refresh_device_config_context(device_pk bigint) RETURNS void AS $$
BEGIN
    UPDATE dcim_device
    SET config_context_data = compute_config_context_for_device(device_pk)
    WHERE id = device_pk;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION refresh_vm_config_context(vm_pk bigint) RETURNS void AS $$
BEGIN
    UPDATE virtualization_virtualmachine
    SET config_context_data = compute_config_context_for_vm(vm_pk)
    WHERE id = vm_pk;
END;
$$ LANGUAGE plpgsql;


-- =============================================================================
-- 5. Bulk refresh helpers
-- =============================================================================
CREATE OR REPLACE FUNCTION refresh_all_device_config_contexts() RETURNS void AS $$
BEGIN
    UPDATE dcim_device SET config_context_data = compute_config_context_for_device(id);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION refresh_all_vm_config_contexts() RETURNS void AS $$
BEGIN
    UPDATE virtualization_virtualmachine SET config_context_data = compute_config_context_for_vm(id);
END;
$$ LANGUAGE plpgsql;


-- =============================================================================
-- CATEGORY A: Device/VM attribute change triggers
-- =============================================================================

-- A1: Device INSERT
CREATE OR REPLACE FUNCTION trg_device_insert_config_context() RETURNS trigger AS $$
BEGIN
    PERFORM refresh_device_config_context(NEW.id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_device_config_context_insert
    AFTER INSERT ON dcim_device
    FOR EACH ROW
    EXECUTE FUNCTION trg_device_insert_config_context();

-- A2: Device UPDATE
CREATE OR REPLACE FUNCTION trg_device_update_config_context() RETURNS trigger AS $$
BEGIN
    PERFORM refresh_device_config_context(NEW.id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_device_config_context_update
    AFTER UPDATE ON dcim_device
    FOR EACH ROW
    WHEN (
        OLD.site_id IS DISTINCT FROM NEW.site_id OR
        OLD.location_id IS DISTINCT FROM NEW.location_id OR
        OLD.role_id IS DISTINCT FROM NEW.role_id OR
        OLD.platform_id IS DISTINCT FROM NEW.platform_id OR
        OLD.cluster_id IS DISTINCT FROM NEW.cluster_id OR
        OLD.tenant_id IS DISTINCT FROM NEW.tenant_id OR
        OLD.device_type_id IS DISTINCT FROM NEW.device_type_id OR
        OLD.local_context_data IS DISTINCT FROM NEW.local_context_data
    )
    EXECUTE FUNCTION trg_device_update_config_context();

-- A3: VM INSERT
CREATE OR REPLACE FUNCTION trg_vm_insert_config_context() RETURNS trigger AS $$
BEGIN
    PERFORM refresh_vm_config_context(NEW.id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_vm_config_context_insert
    AFTER INSERT ON virtualization_virtualmachine
    FOR EACH ROW
    EXECUTE FUNCTION trg_vm_insert_config_context();

-- A4: VM UPDATE
CREATE OR REPLACE FUNCTION trg_vm_update_config_context() RETURNS trigger AS $$
BEGIN
    PERFORM refresh_vm_config_context(NEW.id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_vm_config_context_update
    AFTER UPDATE ON virtualization_virtualmachine
    FOR EACH ROW
    WHEN (
        OLD.site_id IS DISTINCT FROM NEW.site_id OR
        OLD.role_id IS DISTINCT FROM NEW.role_id OR
        OLD.platform_id IS DISTINCT FROM NEW.platform_id OR
        OLD.cluster_id IS DISTINCT FROM NEW.cluster_id OR
        OLD.tenant_id IS DISTINCT FROM NEW.tenant_id OR
        OLD.local_context_data IS DISTINCT FROM NEW.local_context_data
    )
    EXECUTE FUNCTION trg_vm_update_config_context();


-- =============================================================================
-- CATEGORY B: ConfigContext direct changes
-- =============================================================================

CREATE OR REPLACE FUNCTION trg_configcontext_change_refresh_all() RETURNS trigger AS $$
BEGIN
    PERFORM refresh_all_device_config_contexts();
    PERFORM refresh_all_vm_config_contexts();
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_configcontext_insert
    AFTER INSERT ON extras_configcontext
    FOR EACH ROW
    EXECUTE FUNCTION trg_configcontext_change_refresh_all();

CREATE TRIGGER trg_configcontext_delete
    AFTER DELETE ON extras_configcontext
    FOR EACH ROW
    EXECUTE FUNCTION trg_configcontext_change_refresh_all();

CREATE OR REPLACE FUNCTION trg_configcontext_update_refresh_all() RETURNS trigger AS $$
BEGIN
    PERFORM refresh_all_device_config_contexts();
    PERFORM refresh_all_vm_config_contexts();
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_configcontext_update
    AFTER UPDATE ON extras_configcontext
    FOR EACH ROW
    WHEN (
        OLD.data IS DISTINCT FROM NEW.data OR
        OLD.weight IS DISTINCT FROM NEW.weight OR
        OLD.is_active IS DISTINCT FROM NEW.is_active OR
        OLD.name IS DISTINCT FROM NEW.name
    )
    EXECUTE FUNCTION trg_configcontext_update_refresh_all();


-- =============================================================================
-- CATEGORY C: ConfigContext M2M assignment changes
-- =============================================================================

CREATE OR REPLACE FUNCTION trg_configcontext_m2m_refresh_all() RETURNS trigger AS $$
BEGIN
    PERFORM refresh_all_device_config_contexts();
    PERFORM refresh_all_vm_config_contexts();
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- regions
CREATE TRIGGER trg_cc_regions_insert AFTER INSERT ON extras_configcontext_regions
    FOR EACH STATEMENT EXECUTE FUNCTION trg_configcontext_m2m_refresh_all();
CREATE TRIGGER trg_cc_regions_delete AFTER DELETE ON extras_configcontext_regions
    FOR EACH STATEMENT EXECUTE FUNCTION trg_configcontext_m2m_refresh_all();

-- site_groups
CREATE TRIGGER trg_cc_site_groups_insert AFTER INSERT ON extras_configcontext_site_groups
    FOR EACH STATEMENT EXECUTE FUNCTION trg_configcontext_m2m_refresh_all();
CREATE TRIGGER trg_cc_site_groups_delete AFTER DELETE ON extras_configcontext_site_groups
    FOR EACH STATEMENT EXECUTE FUNCTION trg_configcontext_m2m_refresh_all();

-- sites
CREATE TRIGGER trg_cc_sites_insert AFTER INSERT ON extras_configcontext_sites
    FOR EACH STATEMENT EXECUTE FUNCTION trg_configcontext_m2m_refresh_all();
CREATE TRIGGER trg_cc_sites_delete AFTER DELETE ON extras_configcontext_sites
    FOR EACH STATEMENT EXECUTE FUNCTION trg_configcontext_m2m_refresh_all();

-- locations
CREATE TRIGGER trg_cc_locations_insert AFTER INSERT ON extras_configcontext_locations
    FOR EACH STATEMENT EXECUTE FUNCTION trg_configcontext_m2m_refresh_all();
CREATE TRIGGER trg_cc_locations_delete AFTER DELETE ON extras_configcontext_locations
    FOR EACH STATEMENT EXECUTE FUNCTION trg_configcontext_m2m_refresh_all();

-- device_types
CREATE TRIGGER trg_cc_device_types_insert AFTER INSERT ON extras_configcontext_device_types
    FOR EACH STATEMENT EXECUTE FUNCTION trg_configcontext_m2m_refresh_all();
CREATE TRIGGER trg_cc_device_types_delete AFTER DELETE ON extras_configcontext_device_types
    FOR EACH STATEMENT EXECUTE FUNCTION trg_configcontext_m2m_refresh_all();

-- roles
CREATE TRIGGER trg_cc_roles_insert AFTER INSERT ON extras_configcontext_roles
    FOR EACH STATEMENT EXECUTE FUNCTION trg_configcontext_m2m_refresh_all();
CREATE TRIGGER trg_cc_roles_delete AFTER DELETE ON extras_configcontext_roles
    FOR EACH STATEMENT EXECUTE FUNCTION trg_configcontext_m2m_refresh_all();

-- platforms
CREATE TRIGGER trg_cc_platforms_insert AFTER INSERT ON extras_configcontext_platforms
    FOR EACH STATEMENT EXECUTE FUNCTION trg_configcontext_m2m_refresh_all();
CREATE TRIGGER trg_cc_platforms_delete AFTER DELETE ON extras_configcontext_platforms
    FOR EACH STATEMENT EXECUTE FUNCTION trg_configcontext_m2m_refresh_all();

-- cluster_types
CREATE TRIGGER trg_cc_cluster_types_insert AFTER INSERT ON extras_configcontext_cluster_types
    FOR EACH STATEMENT EXECUTE FUNCTION trg_configcontext_m2m_refresh_all();
CREATE TRIGGER trg_cc_cluster_types_delete AFTER DELETE ON extras_configcontext_cluster_types
    FOR EACH STATEMENT EXECUTE FUNCTION trg_configcontext_m2m_refresh_all();

-- cluster_groups
CREATE TRIGGER trg_cc_cluster_groups_insert AFTER INSERT ON extras_configcontext_cluster_groups
    FOR EACH STATEMENT EXECUTE FUNCTION trg_configcontext_m2m_refresh_all();
CREATE TRIGGER trg_cc_cluster_groups_delete AFTER DELETE ON extras_configcontext_cluster_groups
    FOR EACH STATEMENT EXECUTE FUNCTION trg_configcontext_m2m_refresh_all();

-- clusters
CREATE TRIGGER trg_cc_clusters_insert AFTER INSERT ON extras_configcontext_clusters
    FOR EACH STATEMENT EXECUTE FUNCTION trg_configcontext_m2m_refresh_all();
CREATE TRIGGER trg_cc_clusters_delete AFTER DELETE ON extras_configcontext_clusters
    FOR EACH STATEMENT EXECUTE FUNCTION trg_configcontext_m2m_refresh_all();

-- tenant_groups
CREATE TRIGGER trg_cc_tenant_groups_insert AFTER INSERT ON extras_configcontext_tenant_groups
    FOR EACH STATEMENT EXECUTE FUNCTION trg_configcontext_m2m_refresh_all();
CREATE TRIGGER trg_cc_tenant_groups_delete AFTER DELETE ON extras_configcontext_tenant_groups
    FOR EACH STATEMENT EXECUTE FUNCTION trg_configcontext_m2m_refresh_all();

-- tenants
CREATE TRIGGER trg_cc_tenants_insert AFTER INSERT ON extras_configcontext_tenants
    FOR EACH STATEMENT EXECUTE FUNCTION trg_configcontext_m2m_refresh_all();
CREATE TRIGGER trg_cc_tenants_delete AFTER DELETE ON extras_configcontext_tenants
    FOR EACH STATEMENT EXECUTE FUNCTION trg_configcontext_m2m_refresh_all();

-- tags
CREATE TRIGGER trg_cc_tags_insert AFTER INSERT ON extras_configcontext_tags
    FOR EACH STATEMENT EXECUTE FUNCTION trg_configcontext_m2m_refresh_all();
CREATE TRIGGER trg_cc_tags_delete AFTER DELETE ON extras_configcontext_tags
    FOR EACH STATEMENT EXECUTE FUNCTION trg_configcontext_m2m_refresh_all();


-- =============================================================================
-- CATEGORY D: Hierarchical/related model changes
-- =============================================================================

-- D1: Site (region_id or group_id changes)
CREATE OR REPLACE FUNCTION trg_site_update_config_context() RETURNS trigger AS $$
BEGIN
    UPDATE dcim_device SET config_context_data = compute_config_context_for_device(id)
    WHERE site_id = NEW.id;
    UPDATE virtualization_virtualmachine SET config_context_data = compute_config_context_for_vm(id)
    WHERE site_id = NEW.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_site_config_context_update
    AFTER UPDATE ON dcim_site
    FOR EACH ROW
    WHEN (
        OLD.region_id IS DISTINCT FROM NEW.region_id OR
        OLD.group_id IS DISTINCT FROM NEW.group_id
    )
    EXECUTE FUNCTION trg_site_update_config_context();

-- D2: Cluster (type_id or group_id changes)
CREATE OR REPLACE FUNCTION trg_cluster_update_config_context() RETURNS trigger AS $$
BEGIN
    UPDATE dcim_device SET config_context_data = compute_config_context_for_device(id)
    WHERE cluster_id = NEW.id;
    UPDATE virtualization_virtualmachine SET config_context_data = compute_config_context_for_vm(id)
    WHERE cluster_id = NEW.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_cluster_config_context_update
    AFTER UPDATE ON virtualization_cluster
    FOR EACH ROW
    WHEN (
        OLD.type_id IS DISTINCT FROM NEW.type_id OR
        OLD.group_id IS DISTINCT FROM NEW.group_id
    )
    EXECUTE FUNCTION trg_cluster_update_config_context();

-- D3: Tenant (group_id changes)
CREATE OR REPLACE FUNCTION trg_tenant_update_config_context() RETURNS trigger AS $$
BEGIN
    UPDATE dcim_device SET config_context_data = compute_config_context_for_device(id)
    WHERE tenant_id = NEW.id;
    UPDATE virtualization_virtualmachine SET config_context_data = compute_config_context_for_vm(id)
    WHERE tenant_id = NEW.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_tenant_config_context_update
    AFTER UPDATE ON tenancy_tenant
    FOR EACH ROW
    WHEN (OLD.group_id IS DISTINCT FROM NEW.group_id)
    EXECUTE FUNCTION trg_tenant_update_config_context();

-- D4: Region (MPTT fields change)
CREATE OR REPLACE FUNCTION trg_region_update_config_context() RETURNS trigger AS $$
BEGIN
    UPDATE dcim_device SET config_context_data = compute_config_context_for_device(dcim_device.id)
    FROM dcim_site WHERE dcim_device.site_id = dcim_site.id AND dcim_site.region_id = NEW.id;
    UPDATE virtualization_virtualmachine SET config_context_data = compute_config_context_for_vm(virtualization_virtualmachine.id)
    FROM dcim_site WHERE virtualization_virtualmachine.site_id = dcim_site.id AND dcim_site.region_id = NEW.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_region_config_context_update
    AFTER UPDATE ON dcim_region
    FOR EACH ROW
    WHEN (
        OLD.lft IS DISTINCT FROM NEW.lft OR
        OLD.rght IS DISTINCT FROM NEW.rght OR
        OLD.tree_id IS DISTINCT FROM NEW.tree_id OR
        OLD.level IS DISTINCT FROM NEW.level OR
        OLD.parent_id IS DISTINCT FROM NEW.parent_id
    )
    EXECUTE FUNCTION trg_region_update_config_context();

-- D5: SiteGroup (MPTT fields change)
CREATE OR REPLACE FUNCTION trg_sitegroup_update_config_context() RETURNS trigger AS $$
BEGIN
    UPDATE dcim_device SET config_context_data = compute_config_context_for_device(dcim_device.id)
    FROM dcim_site WHERE dcim_device.site_id = dcim_site.id AND dcim_site.group_id = NEW.id;
    UPDATE virtualization_virtualmachine SET config_context_data = compute_config_context_for_vm(virtualization_virtualmachine.id)
    FROM dcim_site WHERE virtualization_virtualmachine.site_id = dcim_site.id AND dcim_site.group_id = NEW.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_sitegroup_config_context_update
    AFTER UPDATE ON dcim_sitegroup
    FOR EACH ROW
    WHEN (
        OLD.lft IS DISTINCT FROM NEW.lft OR
        OLD.rght IS DISTINCT FROM NEW.rght OR
        OLD.tree_id IS DISTINCT FROM NEW.tree_id OR
        OLD.level IS DISTINCT FROM NEW.level OR
        OLD.parent_id IS DISTINCT FROM NEW.parent_id
    )
    EXECUTE FUNCTION trg_sitegroup_update_config_context();

-- D6: DeviceRole (MPTT fields change)
CREATE OR REPLACE FUNCTION trg_devicerole_update_config_context() RETURNS trigger AS $$
BEGIN
    UPDATE dcim_device SET config_context_data = compute_config_context_for_device(id)
    WHERE role_id = NEW.id;
    UPDATE virtualization_virtualmachine SET config_context_data = compute_config_context_for_vm(id)
    WHERE role_id = NEW.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_devicerole_config_context_update
    AFTER UPDATE ON dcim_devicerole
    FOR EACH ROW
    WHEN (
        OLD.lft IS DISTINCT FROM NEW.lft OR
        OLD.rght IS DISTINCT FROM NEW.rght OR
        OLD.tree_id IS DISTINCT FROM NEW.tree_id OR
        OLD.level IS DISTINCT FROM NEW.level OR
        OLD.parent_id IS DISTINCT FROM NEW.parent_id
    )
    EXECUTE FUNCTION trg_devicerole_update_config_context();

-- D7: Platform (MPTT fields change)
CREATE OR REPLACE FUNCTION trg_platform_update_config_context() RETURNS trigger AS $$
BEGIN
    UPDATE dcim_device SET config_context_data = compute_config_context_for_device(id)
    WHERE platform_id = NEW.id;
    UPDATE virtualization_virtualmachine SET config_context_data = compute_config_context_for_vm(id)
    WHERE platform_id = NEW.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_platform_config_context_update
    AFTER UPDATE ON dcim_platform
    FOR EACH ROW
    WHEN (
        OLD.lft IS DISTINCT FROM NEW.lft OR
        OLD.rght IS DISTINCT FROM NEW.rght OR
        OLD.tree_id IS DISTINCT FROM NEW.tree_id OR
        OLD.level IS DISTINCT FROM NEW.level OR
        OLD.parent_id IS DISTINCT FROM NEW.parent_id
    )
    EXECUTE FUNCTION trg_platform_update_config_context();

-- D8: Location (MPTT fields change)
CREATE OR REPLACE FUNCTION trg_location_update_config_context() RETURNS trigger AS $$
BEGIN
    UPDATE dcim_device SET config_context_data = compute_config_context_for_device(id)
    WHERE location_id = NEW.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_location_config_context_update
    AFTER UPDATE ON dcim_location
    FOR EACH ROW
    WHEN (
        OLD.lft IS DISTINCT FROM NEW.lft OR
        OLD.rght IS DISTINCT FROM NEW.rght OR
        OLD.tree_id IS DISTINCT FROM NEW.tree_id OR
        OLD.level IS DISTINCT FROM NEW.level OR
        OLD.parent_id IS DISTINCT FROM NEW.parent_id
    )
    EXECUTE FUNCTION trg_location_update_config_context();


-- =============================================================================
-- CATEGORY E: Tag changes on devices/VMs
-- =============================================================================

CREATE OR REPLACE FUNCTION trg_taggeditem_config_context() RETURNS trigger AS $$
DECLARE
    item record;
    device_ct_id integer;
    vm_ct_id integer;
BEGIN
    IF TG_OP = 'DELETE' THEN
        item := OLD;
    ELSE
        item := NEW;
    END IF;

    SELECT id INTO device_ct_id FROM django_content_type
    WHERE app_label = 'dcim' AND model = 'device';

    SELECT id INTO vm_ct_id FROM django_content_type
    WHERE app_label = 'virtualization' AND model = 'virtualmachine';

    IF item.content_type_id = device_ct_id THEN
        PERFORM refresh_device_config_context(item.object_id);
    ELSIF item.content_type_id = vm_ct_id THEN
        PERFORM refresh_vm_config_context(item.object_id);
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_taggeditem_config_context_insert
    AFTER INSERT ON extras_taggeditem
    FOR EACH ROW
    EXECUTE FUNCTION trg_taggeditem_config_context();

CREATE TRIGGER trg_taggeditem_config_context_delete
    AFTER DELETE ON extras_taggeditem
    FOR EACH ROW
    EXECUTE FUNCTION trg_taggeditem_config_context();
"""


REVERSE_SQL = """
-- Drop all triggers
DROP TRIGGER IF EXISTS trg_device_config_context_insert ON dcim_device;
DROP TRIGGER IF EXISTS trg_device_config_context_update ON dcim_device;
DROP TRIGGER IF EXISTS trg_vm_config_context_insert ON virtualization_virtualmachine;
DROP TRIGGER IF EXISTS trg_vm_config_context_update ON virtualization_virtualmachine;
DROP TRIGGER IF EXISTS trg_configcontext_insert ON extras_configcontext;
DROP TRIGGER IF EXISTS trg_configcontext_delete ON extras_configcontext;
DROP TRIGGER IF EXISTS trg_configcontext_update ON extras_configcontext;
DROP TRIGGER IF EXISTS trg_cc_regions_insert ON extras_configcontext_regions;
DROP TRIGGER IF EXISTS trg_cc_regions_delete ON extras_configcontext_regions;
DROP TRIGGER IF EXISTS trg_cc_site_groups_insert ON extras_configcontext_site_groups;
DROP TRIGGER IF EXISTS trg_cc_site_groups_delete ON extras_configcontext_site_groups;
DROP TRIGGER IF EXISTS trg_cc_sites_insert ON extras_configcontext_sites;
DROP TRIGGER IF EXISTS trg_cc_sites_delete ON extras_configcontext_sites;
DROP TRIGGER IF EXISTS trg_cc_locations_insert ON extras_configcontext_locations;
DROP TRIGGER IF EXISTS trg_cc_locations_delete ON extras_configcontext_locations;
DROP TRIGGER IF EXISTS trg_cc_device_types_insert ON extras_configcontext_device_types;
DROP TRIGGER IF EXISTS trg_cc_device_types_delete ON extras_configcontext_device_types;
DROP TRIGGER IF EXISTS trg_cc_roles_insert ON extras_configcontext_roles;
DROP TRIGGER IF EXISTS trg_cc_roles_delete ON extras_configcontext_roles;
DROP TRIGGER IF EXISTS trg_cc_platforms_insert ON extras_configcontext_platforms;
DROP TRIGGER IF EXISTS trg_cc_platforms_delete ON extras_configcontext_platforms;
DROP TRIGGER IF EXISTS trg_cc_cluster_types_insert ON extras_configcontext_cluster_types;
DROP TRIGGER IF EXISTS trg_cc_cluster_types_delete ON extras_configcontext_cluster_types;
DROP TRIGGER IF EXISTS trg_cc_cluster_groups_insert ON extras_configcontext_cluster_groups;
DROP TRIGGER IF EXISTS trg_cc_cluster_groups_delete ON extras_configcontext_cluster_groups;
DROP TRIGGER IF EXISTS trg_cc_clusters_insert ON extras_configcontext_clusters;
DROP TRIGGER IF EXISTS trg_cc_clusters_delete ON extras_configcontext_clusters;
DROP TRIGGER IF EXISTS trg_cc_tenant_groups_insert ON extras_configcontext_tenant_groups;
DROP TRIGGER IF EXISTS trg_cc_tenant_groups_delete ON extras_configcontext_tenant_groups;
DROP TRIGGER IF EXISTS trg_cc_tenants_insert ON extras_configcontext_tenants;
DROP TRIGGER IF EXISTS trg_cc_tenants_delete ON extras_configcontext_tenants;
DROP TRIGGER IF EXISTS trg_cc_tags_insert ON extras_configcontext_tags;
DROP TRIGGER IF EXISTS trg_cc_tags_delete ON extras_configcontext_tags;
DROP TRIGGER IF EXISTS trg_site_config_context_update ON dcim_site;
DROP TRIGGER IF EXISTS trg_cluster_config_context_update ON virtualization_cluster;
DROP TRIGGER IF EXISTS trg_tenant_config_context_update ON tenancy_tenant;
DROP TRIGGER IF EXISTS trg_region_config_context_update ON dcim_region;
DROP TRIGGER IF EXISTS trg_sitegroup_config_context_update ON dcim_sitegroup;
DROP TRIGGER IF EXISTS trg_devicerole_config_context_update ON dcim_devicerole;
DROP TRIGGER IF EXISTS trg_platform_config_context_update ON dcim_platform;
DROP TRIGGER IF EXISTS trg_location_config_context_update ON dcim_location;
DROP TRIGGER IF EXISTS trg_taggeditem_config_context_insert ON extras_taggeditem;
DROP TRIGGER IF EXISTS trg_taggeditem_config_context_delete ON extras_taggeditem;

-- Drop all trigger functions
DROP FUNCTION IF EXISTS trg_device_insert_config_context();
DROP FUNCTION IF EXISTS trg_device_update_config_context();
DROP FUNCTION IF EXISTS trg_vm_insert_config_context();
DROP FUNCTION IF EXISTS trg_vm_update_config_context();
DROP FUNCTION IF EXISTS trg_configcontext_change_refresh_all();
DROP FUNCTION IF EXISTS trg_configcontext_update_refresh_all();
DROP FUNCTION IF EXISTS trg_configcontext_m2m_refresh_all();
DROP FUNCTION IF EXISTS trg_site_update_config_context();
DROP FUNCTION IF EXISTS trg_cluster_update_config_context();
DROP FUNCTION IF EXISTS trg_tenant_update_config_context();
DROP FUNCTION IF EXISTS trg_region_update_config_context();
DROP FUNCTION IF EXISTS trg_sitegroup_update_config_context();
DROP FUNCTION IF EXISTS trg_devicerole_update_config_context();
DROP FUNCTION IF EXISTS trg_platform_update_config_context();
DROP FUNCTION IF EXISTS trg_location_update_config_context();
DROP FUNCTION IF EXISTS trg_taggeditem_config_context();

-- Drop helper functions
DROP FUNCTION IF EXISTS refresh_all_vm_config_contexts();
DROP FUNCTION IF EXISTS refresh_all_device_config_contexts();
DROP FUNCTION IF EXISTS refresh_vm_config_context(bigint);
DROP FUNCTION IF EXISTS refresh_device_config_context(bigint);
DROP FUNCTION IF EXISTS compute_config_context_for_vm(bigint);
DROP FUNCTION IF EXISTS compute_config_context_for_device(bigint);
DROP FUNCTION IF EXISTS jsonb_deepmerge(jsonb, jsonb);
"""


POPULATE_SQL = """
UPDATE dcim_device SET config_context_data = compute_config_context_for_device(id);
UPDATE virtualization_virtualmachine SET config_context_data = compute_config_context_for_vm(id);
"""

CLEAR_SQL = """
UPDATE dcim_device SET config_context_data = NULL;
UPDATE virtualization_virtualmachine SET config_context_data = NULL;
"""


class Migration(migrations.Migration):
    dependencies = [
        ('extras', '0134_owner'),
        ('dcim', '0227_device_config_context_data'),
        ('virtualization', '0053_virtualmachine_config_context_data'),
        ('tenancy', '0023_add_mptt_tree_indexes'),
    ]

    operations = [
        migrations.RunSQL(
            sql=FORWARD_SQL,
            reverse_sql=REVERSE_SQL,
        ),
        migrations.RunSQL(
            sql=POPULATE_SQL,
            reverse_sql=CLEAR_SQL,
        ),
    ]
