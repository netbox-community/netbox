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
-- When a prefix changes, reassign any IPAddresses that no longer
-- fall within the new prefix range to the parent prefix (or set null if no parent exists)
UPDATE ipam_prefix
SET parent_id = OLD.parent_id
WHERE
    parent_id = NEW.id
    -- IP address no longer contained within the updated prefix
    AND NOT (prefix << NEW.prefix);

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
