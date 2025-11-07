ipam_prefix_delete_adjust_prefix_parent = """
-- Update Child Prefix's with Prefix's PARENT
UPDATE ipam_prefix SET parent_id=OLD.parent_id WHERE parent_id=OLD.id;
RETURN OLD;
"""


ipam_prefix_delete_adjust_ipaddress_prefix = """
-- Update IP Address with prefix's PARENT
UPDATE ipam_ipaddress SET prefix_id=OLD.parent_id WHERE prefix_id=OLD.id;
RETURN OLD;
"""


ipam_prefix_delete_adjust_iprange_prefix = """
-- Update IP Range with prefix's PARENT
UPDATE ipam_iprange SET prefix_id=OLD.parent_id WHERE prefix_id=OLD.id;
RETURN OLD;
"""


ipam_prefix_insert_adjust_prefix_parent = """
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


ipam_prefix_insert_adjust_ipaddress_prefix = """
UPDATE ipam_prefix
SET prefix_id=NEW.id
WHERE
    NEW.prefix >> ipaddress.address
    AND
    (
        (NEW.vrf = ipaddress.vrf_id OR (NEW.vrf_id IS NULL and ipaddress.vrf_id IS NULL))
        OR
        (NEW.vrf_id IS NULL AND NEW.status = 'container')
    )
    AND (
        ipaddress.prefix_id IS NULL
        OR
        EXISTS (
            SELECT 1 from prefix p WHERE
                p.id = ipaddress.prefix_id
                AND NEW.prefix << p.prefix
        )
    )
    AND 
        -- Check to ensure current parent PREFIX is not in a VRF
        NOT EXISTS (
            SELECT 1 from prefix p WHERE (
                p.id = ipaddress.prefix_id
                AND
                p.vrf_id IS NOT NULL
                AND
                ipaddress.vrf_id IS NOT NULL
                AND
                (
                    NEW.vrf_id IS NULL AND NEW.status = 'container'
                )
            )
        )
    AND
     NOT EXISTS (
        SELECT 1 FROM prefix p
        WHERE
        p.prefix >> ipaddress.address
        AND p.id != NEW.id
        AND p.prefix << NEW.prefix
        AND (
            (p.vrf_id = ipaddress.vrf_id OR (p.vrf_id IS NULL AND ipaddress.vrf_id IS NULL))
            OR
            (p.vrf_id IS NULL AND NEW.status = 'container')
        )
     );
RETURN NEW;
"""
