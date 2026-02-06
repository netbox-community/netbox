ipam_prefix_delete_adjust_prefix_parent = """
-- Update Child Prefix's with Prefix's PARENT  This is a safe assumption based on the fact that the parent would be the
-- next direct parent for anything else that could contain this prefix
UPDATE ipam_prefix SET parent_id=OLD.parent_id WHERE parent_id=OLD.id;
RETURN OLD;
"""


ipam_prefix_insert_adjust_prefix_parent = """
-- Update the prefix with the new parent if the parent is the most appropriate prefix
UPDATE ipam_prefix
SET parent_id=NEW.id
WHERE
    prefix << NEW.prefix
    AND
    (
        (vrf_id = NEW.vrf_id OR (vrf_id IS NULL AND NEW.vrf_id IS NULL))
        OR
        (
            NEW.vrf_id IS NULL
            AND
            NEW.status = 'container'
            AND
            NOT EXISTS(
                SELECT 1 FROM ipam_prefix p WHERE p.prefix >> ipam_prefix.prefix AND p.vrf_id = ipam_prefix.vrf_id
            )
        )
    )
    AND id != NEW.id
    AND NOT EXISTS (
        SELECT 1 FROM ipam_prefix p
        WHERE
            p.prefix >> ipam_prefix.prefix
            AND p.prefix << NEW.prefix
            AND (
                (p.vrf_id = ipam_prefix.vrf_id OR (p.vrf_id IS NULL AND ipam_prefix.vrf_id IS NULL))
                OR
                (p.vrf_id IS NULL AND p.status = 'container')
            )
            AND p.id != NEW.id
    )
;
RETURN NEW;
"""


ipam_prefix_update_adjust_prefix_parent = """
-- When a prefix changes, reassign any child prefixes that no longer
-- fall within the new prefix range to the parent prefix (or set null if no parent exists)
UPDATE ipam_prefix
SET parent_id = OLD.parent_id
WHERE
    parent_id = NEW.id
    -- IP address no longer contained within the updated prefix
    AND NOT (prefix << NEW.prefix);

-- When a prefix changes, reassign any ip addresses that no longer
-- fall within the new prefix range to the parent prefix (or set null if no parent exists)
UPDATE ipam_ipaddress
SET prefix_id = OLD.parent_id
WHERE
    prefix_id = NEW.id
    -- IP address no longer contained within the updated prefix
    AND
    NOT (address << NEW.prefix)
;

-- When a prefix changes, reassign any ip ranges that no longer
-- fall within the new prefix range to the parent prefix (or set null if no parent exists)
UPDATE ipam_iprange
SET prefix_id = OLD.parent_id
WHERE
    prefix_id = NEW.id
    -- IP address no longer contained within the updated prefix
    AND
    NOT (start_address << NEW.prefix)
    AND
    NOT (end_address << NEW.prefix)
;

-- When a prefix changes, reassign any ip addresses that are in-scope but
-- no longer within the same VRF
UPDATE ipam_ipaddress
    SET prefix_id = OLD.parent_id
    WHERE
        prefix_id = NEW.id
        AND
        address << OLD.prefix
        AND
        (
            NOT address << NEW.prefix
            OR
            (
                vrf_id is NULL
                AND
                NEW.vrf_id IS NOT NULL
            )
            OR
            (
                OLD.vrf_id IS NULL
                AND
                NEW.vrf_id IS NOT NULL
                AND
                NEW.vrf_id != vrf_id
            )
        )
;

-- When a prefix changes, reassign any ip ranges that are in-scope but
-- no longer within the same VRF
UPDATE ipam_iprange
    SET prefix_id = OLD.parent_id
    WHERE
        prefix_id = NEW.id
        AND
        start_address << OLD.prefix
        AND
        end_address << OLD.prefix
        AND
        (
            NOT start_address << NEW.prefix
            OR
            NOT end_address << NEW.prefix
            OR
            (
                vrf_id is NULL
                AND
                NEW.vrf_id IS NOT NULL
            )
            OR
            (
                OLD.vrf_id IS NULL
                AND
                NEW.vrf_id IS NOT NULL
                AND
                NEW.vrf_id != vrf_id
            )
        )
;

-- Update the prefix with the new parent if the parent is the most appropriate prefix
UPDATE ipam_prefix
    SET parent_id=NEW.id
    WHERE
        prefix << NEW.prefix
        AND
        (
            (vrf_id = NEW.vrf_id OR (vrf_id IS NULL AND NEW.vrf_id IS NULL))
            OR
            (
                NEW.vrf_id IS NULL
                AND
                NEW.status = 'container'
                AND
                NOT EXISTS(
                    SELECT 1 FROM ipam_prefix p WHERE p.prefix >> prefix AND p.vrf_id = vrf_id
                )
            )
        )
        AND id != NEW.id
        AND NOT EXISTS (
            SELECT 1 FROM ipam_prefix p
            WHERE
                p.prefix >> ipam_prefix.prefix
                AND p.prefix << NEW.prefix
                AND (
                    (p.vrf_id = ipam_prefix.vrf_id OR (p.vrf_id IS NULL AND ipam_prefix.vrf_id IS NULL))
                    OR
                    (p.vrf_id IS NULL AND p.status = 'container')
                )
                AND p.id != NEW.id
        )
;
UPDATE ipam_ipaddress
    SET prefix_id = NEW.id
    WHERE
        prefix_id != NEW.id
        AND
        address << NEW.prefix
        AND (
            (vrf_id = NEW.vrf_id OR (vrf_id IS NULL AND NEW.vrf_id IS NULL))
            OR (
                NEW.vrf_id IS NULL
                AND
                NEW.status = 'container'
                AND
                NOT EXISTS(
                    SELECT 1 FROM ipam_prefix p WHERE p.prefix >> address AND p.vrf_id = vrf_id
                )
            )
        )
;
UPDATE ipam_iprange
    SET prefix_id = NEW.id
    WHERE
        prefix_id != NEW.id
        AND
        start_address << NEW.prefix
        AND
        end_address << NEW.prefix
        AND (
            (vrf_id = NEW.vrf_id OR (vrf_id IS NULL AND NEW.vrf_id IS NULL))
            OR (
                NEW.vrf_id IS NULL
                AND
                NEW.status = 'container'
                AND
                NOT EXISTS(
                    SELECT 1 FROM ipam_prefix p WHERE
                        p.prefix >> start_address
                        AND
                        p.prefix >> end_address
                        AND
                        p.vrf_id = vrf_id
                )
            )
        )
;
RETURN NEW;
"""
