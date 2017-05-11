--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.2
-- Dumped by pg_dump version 9.6.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: auth_group; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE auth_group (
    id integer NOT NULL,
    name character varying(80) NOT NULL
);


ALTER TABLE auth_group OWNER TO netbox;

--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE auth_group_id_seq OWNER TO netbox;

--
-- Name: auth_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE auth_group_id_seq OWNED BY auth_group.id;


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE auth_group_permissions (
    id integer NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE auth_group_permissions OWNER TO netbox;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE auth_group_permissions_id_seq OWNER TO netbox;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE auth_group_permissions_id_seq OWNED BY auth_group_permissions.id;


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


ALTER TABLE auth_permission OWNER TO netbox;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE auth_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE auth_permission_id_seq OWNER TO netbox;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE auth_permission_id_seq OWNED BY auth_permission.id;


--
-- Name: auth_user; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE auth_user (
    id integer NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    username character varying(150) NOT NULL,
    first_name character varying(30) NOT NULL,
    last_name character varying(30) NOT NULL,
    email character varying(254) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL
);


ALTER TABLE auth_user OWNER TO netbox;

--
-- Name: auth_user_groups; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE auth_user_groups (
    id integer NOT NULL,
    user_id integer NOT NULL,
    group_id integer NOT NULL
);


ALTER TABLE auth_user_groups OWNER TO netbox;

--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE auth_user_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE auth_user_groups_id_seq OWNER TO netbox;

--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE auth_user_groups_id_seq OWNED BY auth_user_groups.id;


--
-- Name: auth_user_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE auth_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE auth_user_id_seq OWNER TO netbox;

--
-- Name: auth_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE auth_user_id_seq OWNED BY auth_user.id;


--
-- Name: auth_user_user_permissions; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE auth_user_user_permissions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE auth_user_user_permissions OWNER TO netbox;

--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE auth_user_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE auth_user_user_permissions_id_seq OWNER TO netbox;

--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE auth_user_user_permissions_id_seq OWNED BY auth_user_user_permissions.id;


--
-- Name: circuits_circuit; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE circuits_circuit (
    id integer NOT NULL,
    created date NOT NULL,
    last_updated timestamp with time zone NOT NULL,
    cid character varying(50) NOT NULL,
    install_date date,
    commit_rate integer,
    comments text NOT NULL,
    provider_id integer NOT NULL,
    type_id integer NOT NULL,
    tenant_id integer,
    description character varying(100) NOT NULL,
    CONSTRAINT circuits_circuit_commit_rate_check CHECK ((commit_rate >= 0))
);


ALTER TABLE circuits_circuit OWNER TO netbox;

--
-- Name: circuits_circuit_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE circuits_circuit_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE circuits_circuit_id_seq OWNER TO netbox;

--
-- Name: circuits_circuit_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE circuits_circuit_id_seq OWNED BY circuits_circuit.id;


--
-- Name: circuits_circuittermination; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE circuits_circuittermination (
    id integer NOT NULL,
    term_side character varying(1) NOT NULL,
    port_speed integer NOT NULL,
    upstream_speed integer,
    xconnect_id character varying(50) NOT NULL,
    pp_info character varying(100) NOT NULL,
    circuit_id integer NOT NULL,
    interface_id integer,
    site_id integer NOT NULL,
    CONSTRAINT circuits_circuittermination_port_speed_check CHECK ((port_speed >= 0)),
    CONSTRAINT circuits_circuittermination_upstream_speed_check CHECK ((upstream_speed >= 0))
);


ALTER TABLE circuits_circuittermination OWNER TO netbox;

--
-- Name: circuits_circuittermination_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE circuits_circuittermination_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE circuits_circuittermination_id_seq OWNER TO netbox;

--
-- Name: circuits_circuittermination_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE circuits_circuittermination_id_seq OWNED BY circuits_circuittermination.id;


--
-- Name: circuits_circuittype; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE circuits_circuittype (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    slug character varying(50) NOT NULL
);


ALTER TABLE circuits_circuittype OWNER TO netbox;

--
-- Name: circuits_circuittype_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE circuits_circuittype_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE circuits_circuittype_id_seq OWNER TO netbox;

--
-- Name: circuits_circuittype_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE circuits_circuittype_id_seq OWNED BY circuits_circuittype.id;


--
-- Name: circuits_provider; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE circuits_provider (
    id integer NOT NULL,
    created date NOT NULL,
    last_updated timestamp with time zone NOT NULL,
    name character varying(50) NOT NULL,
    slug character varying(50) NOT NULL,
    asn bigint,
    account character varying(30) NOT NULL,
    portal_url character varying(200) NOT NULL,
    noc_contact text NOT NULL,
    admin_contact text NOT NULL,
    comments text NOT NULL
);


ALTER TABLE circuits_provider OWNER TO netbox;

--
-- Name: circuits_provider_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE circuits_provider_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE circuits_provider_id_seq OWNER TO netbox;

--
-- Name: circuits_provider_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE circuits_provider_id_seq OWNED BY circuits_provider.id;


--
-- Name: dcim_consoleport; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE dcim_consoleport (
    id integer NOT NULL,
    name character varying(30) NOT NULL,
    connection_status boolean,
    cs_port_id integer,
    device_id integer NOT NULL
);


ALTER TABLE dcim_consoleport OWNER TO netbox;

--
-- Name: dcim_consoleport_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE dcim_consoleport_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE dcim_consoleport_id_seq OWNER TO netbox;

--
-- Name: dcim_consoleport_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE dcim_consoleport_id_seq OWNED BY dcim_consoleport.id;


--
-- Name: dcim_consoleporttemplate; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE dcim_consoleporttemplate (
    id integer NOT NULL,
    name character varying(30) NOT NULL,
    device_type_id integer NOT NULL
);


ALTER TABLE dcim_consoleporttemplate OWNER TO netbox;

--
-- Name: dcim_consoleporttemplate_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE dcim_consoleporttemplate_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE dcim_consoleporttemplate_id_seq OWNER TO netbox;

--
-- Name: dcim_consoleporttemplate_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE dcim_consoleporttemplate_id_seq OWNED BY dcim_consoleporttemplate.id;


--
-- Name: dcim_consoleserverport; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE dcim_consoleserverport (
    id integer NOT NULL,
    name character varying(30) NOT NULL,
    device_id integer NOT NULL
);


ALTER TABLE dcim_consoleserverport OWNER TO netbox;

--
-- Name: dcim_consoleserverport_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE dcim_consoleserverport_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE dcim_consoleserverport_id_seq OWNER TO netbox;

--
-- Name: dcim_consoleserverport_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE dcim_consoleserverport_id_seq OWNED BY dcim_consoleserverport.id;


--
-- Name: dcim_consoleserverporttemplate; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE dcim_consoleserverporttemplate (
    id integer NOT NULL,
    name character varying(30) NOT NULL,
    device_type_id integer NOT NULL
);


ALTER TABLE dcim_consoleserverporttemplate OWNER TO netbox;

--
-- Name: dcim_consoleserverporttemplate_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE dcim_consoleserverporttemplate_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE dcim_consoleserverporttemplate_id_seq OWNER TO netbox;

--
-- Name: dcim_consoleserverporttemplate_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE dcim_consoleserverporttemplate_id_seq OWNED BY dcim_consoleserverporttemplate.id;


--
-- Name: dcim_device; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE dcim_device (
    id integer NOT NULL,
    created date NOT NULL,
    last_updated timestamp with time zone NOT NULL,
    name character varying(64),
    serial character varying(50) NOT NULL,
    "position" smallint,
    face smallint,
    status boolean NOT NULL,
    comments text NOT NULL,
    device_role_id integer NOT NULL,
    device_type_id integer NOT NULL,
    platform_id integer,
    rack_id integer,
    primary_ip4_id integer,
    primary_ip6_id integer,
    tenant_id integer,
    asset_tag character varying(50),
    site_id integer NOT NULL,
    CONSTRAINT dcim_device_face_check CHECK ((face >= 0)),
    CONSTRAINT dcim_device_position_check CHECK (("position" >= 0))
);


ALTER TABLE dcim_device OWNER TO netbox;

--
-- Name: dcim_device_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE dcim_device_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE dcim_device_id_seq OWNER TO netbox;

--
-- Name: dcim_device_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE dcim_device_id_seq OWNED BY dcim_device.id;


--
-- Name: dcim_devicebay; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE dcim_devicebay (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    device_id integer NOT NULL,
    installed_device_id integer
);


ALTER TABLE dcim_devicebay OWNER TO netbox;

--
-- Name: dcim_devicebay_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE dcim_devicebay_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE dcim_devicebay_id_seq OWNER TO netbox;

--
-- Name: dcim_devicebay_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE dcim_devicebay_id_seq OWNED BY dcim_devicebay.id;


--
-- Name: dcim_devicebaytemplate; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE dcim_devicebaytemplate (
    id integer NOT NULL,
    name character varying(30) NOT NULL,
    device_type_id integer NOT NULL
);


ALTER TABLE dcim_devicebaytemplate OWNER TO netbox;

--
-- Name: dcim_devicebaytemplate_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE dcim_devicebaytemplate_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE dcim_devicebaytemplate_id_seq OWNER TO netbox;

--
-- Name: dcim_devicebaytemplate_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE dcim_devicebaytemplate_id_seq OWNED BY dcim_devicebaytemplate.id;


--
-- Name: dcim_devicerole; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE dcim_devicerole (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    slug character varying(50) NOT NULL,
    color character varying(6) NOT NULL
);


ALTER TABLE dcim_devicerole OWNER TO netbox;

--
-- Name: dcim_devicerole_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE dcim_devicerole_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE dcim_devicerole_id_seq OWNER TO netbox;

--
-- Name: dcim_devicerole_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE dcim_devicerole_id_seq OWNED BY dcim_devicerole.id;


--
-- Name: dcim_devicetype; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE dcim_devicetype (
    id integer NOT NULL,
    model character varying(50) NOT NULL,
    slug character varying(50) NOT NULL,
    u_height smallint NOT NULL,
    is_full_depth boolean NOT NULL,
    is_console_server boolean NOT NULL,
    is_pdu boolean NOT NULL,
    is_network_device boolean NOT NULL,
    manufacturer_id integer NOT NULL,
    subdevice_role boolean,
    part_number character varying(50) NOT NULL,
    comments text NOT NULL,
    interface_ordering smallint NOT NULL,
    CONSTRAINT dcim_devicetype_interface_ordering_check CHECK ((interface_ordering >= 0)),
    CONSTRAINT dcim_devicetype_u_height_check CHECK ((u_height >= 0))
);


ALTER TABLE dcim_devicetype OWNER TO netbox;

--
-- Name: dcim_devicetype_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE dcim_devicetype_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE dcim_devicetype_id_seq OWNER TO netbox;

--
-- Name: dcim_devicetype_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE dcim_devicetype_id_seq OWNED BY dcim_devicetype.id;


--
-- Name: dcim_interface; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE dcim_interface (
    id integer NOT NULL,
    name character varying(30) NOT NULL,
    form_factor smallint NOT NULL,
    mgmt_only boolean NOT NULL,
    description character varying(100) NOT NULL,
    device_id integer NOT NULL,
    mac_address macaddr,
    lag_id integer,
    CONSTRAINT dcim_interface_form_factor_check CHECK ((form_factor >= 0))
);


ALTER TABLE dcim_interface OWNER TO netbox;

--
-- Name: dcim_interface_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE dcim_interface_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE dcim_interface_id_seq OWNER TO netbox;

--
-- Name: dcim_interface_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE dcim_interface_id_seq OWNED BY dcim_interface.id;


--
-- Name: dcim_interfaceconnection; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE dcim_interfaceconnection (
    id integer NOT NULL,
    connection_status boolean NOT NULL,
    interface_a_id integer NOT NULL,
    interface_b_id integer NOT NULL
);


ALTER TABLE dcim_interfaceconnection OWNER TO netbox;

--
-- Name: dcim_interfaceconnection_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE dcim_interfaceconnection_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE dcim_interfaceconnection_id_seq OWNER TO netbox;

--
-- Name: dcim_interfaceconnection_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE dcim_interfaceconnection_id_seq OWNED BY dcim_interfaceconnection.id;


--
-- Name: dcim_interfacetemplate; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE dcim_interfacetemplate (
    id integer NOT NULL,
    name character varying(30) NOT NULL,
    form_factor smallint NOT NULL,
    mgmt_only boolean NOT NULL,
    device_type_id integer NOT NULL,
    CONSTRAINT dcim_interfacetemplate_form_factor_check CHECK ((form_factor >= 0))
);


ALTER TABLE dcim_interfacetemplate OWNER TO netbox;

--
-- Name: dcim_interfacetemplate_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE dcim_interfacetemplate_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE dcim_interfacetemplate_id_seq OWNER TO netbox;

--
-- Name: dcim_interfacetemplate_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE dcim_interfacetemplate_id_seq OWNED BY dcim_interfacetemplate.id;


--
-- Name: dcim_inventoryitem; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE dcim_inventoryitem (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    part_id character varying(50) NOT NULL,
    serial character varying(50) NOT NULL,
    discovered boolean NOT NULL,
    device_id integer NOT NULL,
    parent_id integer,
    manufacturer_id integer
);


ALTER TABLE dcim_inventoryitem OWNER TO netbox;

--
-- Name: dcim_manufacturer; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE dcim_manufacturer (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    slug character varying(50) NOT NULL
);


ALTER TABLE dcim_manufacturer OWNER TO netbox;

--
-- Name: dcim_manufacturer_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE dcim_manufacturer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE dcim_manufacturer_id_seq OWNER TO netbox;

--
-- Name: dcim_manufacturer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE dcim_manufacturer_id_seq OWNED BY dcim_manufacturer.id;


--
-- Name: dcim_module_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE dcim_module_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE dcim_module_id_seq OWNER TO netbox;

--
-- Name: dcim_module_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE dcim_module_id_seq OWNED BY dcim_inventoryitem.id;


--
-- Name: dcim_platform; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE dcim_platform (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    slug character varying(50) NOT NULL,
    rpc_client character varying(30) NOT NULL
);


ALTER TABLE dcim_platform OWNER TO netbox;

--
-- Name: dcim_platform_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE dcim_platform_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE dcim_platform_id_seq OWNER TO netbox;

--
-- Name: dcim_platform_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE dcim_platform_id_seq OWNED BY dcim_platform.id;


--
-- Name: dcim_poweroutlet; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE dcim_poweroutlet (
    id integer NOT NULL,
    name character varying(30) NOT NULL,
    device_id integer NOT NULL
);


ALTER TABLE dcim_poweroutlet OWNER TO netbox;

--
-- Name: dcim_poweroutlet_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE dcim_poweroutlet_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE dcim_poweroutlet_id_seq OWNER TO netbox;

--
-- Name: dcim_poweroutlet_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE dcim_poweroutlet_id_seq OWNED BY dcim_poweroutlet.id;


--
-- Name: dcim_poweroutlettemplate; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE dcim_poweroutlettemplate (
    id integer NOT NULL,
    name character varying(30) NOT NULL,
    device_type_id integer NOT NULL
);


ALTER TABLE dcim_poweroutlettemplate OWNER TO netbox;

--
-- Name: dcim_poweroutlettemplate_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE dcim_poweroutlettemplate_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE dcim_poweroutlettemplate_id_seq OWNER TO netbox;

--
-- Name: dcim_poweroutlettemplate_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE dcim_poweroutlettemplate_id_seq OWNED BY dcim_poweroutlettemplate.id;


--
-- Name: dcim_powerport; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE dcim_powerport (
    id integer NOT NULL,
    name character varying(30) NOT NULL,
    connection_status boolean,
    device_id integer NOT NULL,
    power_outlet_id integer
);


ALTER TABLE dcim_powerport OWNER TO netbox;

--
-- Name: dcim_powerport_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE dcim_powerport_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE dcim_powerport_id_seq OWNER TO netbox;

--
-- Name: dcim_powerport_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE dcim_powerport_id_seq OWNED BY dcim_powerport.id;


--
-- Name: dcim_powerporttemplate; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE dcim_powerporttemplate (
    id integer NOT NULL,
    name character varying(30) NOT NULL,
    device_type_id integer NOT NULL
);


ALTER TABLE dcim_powerporttemplate OWNER TO netbox;

--
-- Name: dcim_powerporttemplate_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE dcim_powerporttemplate_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE dcim_powerporttemplate_id_seq OWNER TO netbox;

--
-- Name: dcim_powerporttemplate_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE dcim_powerporttemplate_id_seq OWNED BY dcim_powerporttemplate.id;


--
-- Name: dcim_rack; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE dcim_rack (
    id integer NOT NULL,
    created date NOT NULL,
    last_updated timestamp with time zone NOT NULL,
    name character varying(50) NOT NULL,
    facility_id character varying(30),
    u_height smallint NOT NULL,
    comments text NOT NULL,
    group_id integer,
    site_id integer NOT NULL,
    tenant_id integer,
    type smallint,
    width smallint NOT NULL,
    role_id integer,
    desc_units boolean NOT NULL,
    CONSTRAINT dcim_rack_type_check CHECK ((type >= 0)),
    CONSTRAINT dcim_rack_u_height_check CHECK ((u_height >= 0)),
    CONSTRAINT dcim_rack_width_check CHECK ((width >= 0))
);


ALTER TABLE dcim_rack OWNER TO netbox;

--
-- Name: dcim_rack_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE dcim_rack_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE dcim_rack_id_seq OWNER TO netbox;

--
-- Name: dcim_rack_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE dcim_rack_id_seq OWNED BY dcim_rack.id;


--
-- Name: dcim_rackgroup; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE dcim_rackgroup (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    slug character varying(50) NOT NULL,
    site_id integer NOT NULL
);


ALTER TABLE dcim_rackgroup OWNER TO netbox;

--
-- Name: dcim_rackgroup_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE dcim_rackgroup_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE dcim_rackgroup_id_seq OWNER TO netbox;

--
-- Name: dcim_rackgroup_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE dcim_rackgroup_id_seq OWNED BY dcim_rackgroup.id;


--
-- Name: dcim_rackreservation; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE dcim_rackreservation (
    id integer NOT NULL,
    units smallint[] NOT NULL,
    created timestamp with time zone NOT NULL,
    description character varying(100) NOT NULL,
    rack_id integer NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE dcim_rackreservation OWNER TO netbox;

--
-- Name: dcim_rackreservation_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE dcim_rackreservation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE dcim_rackreservation_id_seq OWNER TO netbox;

--
-- Name: dcim_rackreservation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE dcim_rackreservation_id_seq OWNED BY dcim_rackreservation.id;


--
-- Name: dcim_rackrole; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE dcim_rackrole (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    slug character varying(50) NOT NULL,
    color character varying(6) NOT NULL
);


ALTER TABLE dcim_rackrole OWNER TO netbox;

--
-- Name: dcim_rackrole_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE dcim_rackrole_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE dcim_rackrole_id_seq OWNER TO netbox;

--
-- Name: dcim_rackrole_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE dcim_rackrole_id_seq OWNED BY dcim_rackrole.id;


--
-- Name: dcim_region; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE dcim_region (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    slug character varying(50) NOT NULL,
    lft integer NOT NULL,
    rght integer NOT NULL,
    tree_id integer NOT NULL,
    level integer NOT NULL,
    parent_id integer,
    CONSTRAINT dcim_region_level_check CHECK ((level >= 0)),
    CONSTRAINT dcim_region_lft_check CHECK ((lft >= 0)),
    CONSTRAINT dcim_region_rght_check CHECK ((rght >= 0)),
    CONSTRAINT dcim_region_tree_id_check CHECK ((tree_id >= 0))
);


ALTER TABLE dcim_region OWNER TO netbox;

--
-- Name: dcim_region_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE dcim_region_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE dcim_region_id_seq OWNER TO netbox;

--
-- Name: dcim_region_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE dcim_region_id_seq OWNED BY dcim_region.id;


--
-- Name: dcim_site; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE dcim_site (
    id integer NOT NULL,
    created date NOT NULL,
    last_updated timestamp with time zone NOT NULL,
    name character varying(50) NOT NULL,
    slug character varying(50) NOT NULL,
    facility character varying(50) NOT NULL,
    asn bigint,
    physical_address character varying(200) NOT NULL,
    shipping_address character varying(200) NOT NULL,
    comments text NOT NULL,
    tenant_id integer,
    contact_email character varying(254) NOT NULL,
    contact_name character varying(50) NOT NULL,
    contact_phone character varying(20) NOT NULL,
    region_id integer
);


ALTER TABLE dcim_site OWNER TO netbox;

--
-- Name: dcim_site_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE dcim_site_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE dcim_site_id_seq OWNER TO netbox;

--
-- Name: dcim_site_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE dcim_site_id_seq OWNED BY dcim_site.id;


--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id integer NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


ALTER TABLE django_admin_log OWNER TO netbox;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE django_admin_log_id_seq OWNER TO netbox;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE django_admin_log_id_seq OWNED BY django_admin_log.id;


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


ALTER TABLE django_content_type OWNER TO netbox;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE django_content_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE django_content_type_id_seq OWNER TO netbox;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE django_content_type_id_seq OWNED BY django_content_type.id;


--
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE django_migrations (
    id integer NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


ALTER TABLE django_migrations OWNER TO netbox;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE django_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE django_migrations_id_seq OWNER TO netbox;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE django_migrations_id_seq OWNED BY django_migrations.id;


--
-- Name: django_session; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


ALTER TABLE django_session OWNER TO netbox;

--
-- Name: extras_customfield; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE extras_customfield (
    id integer NOT NULL,
    type smallint NOT NULL,
    name character varying(50) NOT NULL,
    label character varying(50) NOT NULL,
    description character varying(100) NOT NULL,
    required boolean NOT NULL,
    is_filterable boolean NOT NULL,
    "default" character varying(100) NOT NULL,
    weight smallint NOT NULL,
    CONSTRAINT extras_customfield_type_check CHECK ((type >= 0)),
    CONSTRAINT extras_customfield_weight_check CHECK ((weight >= 0))
);


ALTER TABLE extras_customfield OWNER TO netbox;

--
-- Name: extras_customfield_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE extras_customfield_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE extras_customfield_id_seq OWNER TO netbox;

--
-- Name: extras_customfield_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE extras_customfield_id_seq OWNED BY extras_customfield.id;


--
-- Name: extras_customfield_obj_type; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE extras_customfield_obj_type (
    id integer NOT NULL,
    customfield_id integer NOT NULL,
    contenttype_id integer NOT NULL
);


ALTER TABLE extras_customfield_obj_type OWNER TO netbox;

--
-- Name: extras_customfield_obj_type_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE extras_customfield_obj_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE extras_customfield_obj_type_id_seq OWNER TO netbox;

--
-- Name: extras_customfield_obj_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE extras_customfield_obj_type_id_seq OWNED BY extras_customfield_obj_type.id;


--
-- Name: extras_customfieldchoice; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE extras_customfieldchoice (
    id integer NOT NULL,
    value character varying(100) NOT NULL,
    weight smallint NOT NULL,
    field_id integer NOT NULL,
    CONSTRAINT extras_customfieldchoice_weight_check CHECK ((weight >= 0))
);


ALTER TABLE extras_customfieldchoice OWNER TO netbox;

--
-- Name: extras_customfieldchoice_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE extras_customfieldchoice_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE extras_customfieldchoice_id_seq OWNER TO netbox;

--
-- Name: extras_customfieldchoice_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE extras_customfieldchoice_id_seq OWNED BY extras_customfieldchoice.id;


--
-- Name: extras_customfieldvalue; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE extras_customfieldvalue (
    id integer NOT NULL,
    obj_id integer NOT NULL,
    serialized_value character varying(255) NOT NULL,
    field_id integer NOT NULL,
    obj_type_id integer NOT NULL,
    CONSTRAINT extras_customfieldvalue_obj_id_check CHECK ((obj_id >= 0))
);


ALTER TABLE extras_customfieldvalue OWNER TO netbox;

--
-- Name: extras_customfieldvalue_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE extras_customfieldvalue_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE extras_customfieldvalue_id_seq OWNER TO netbox;

--
-- Name: extras_customfieldvalue_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE extras_customfieldvalue_id_seq OWNED BY extras_customfieldvalue.id;


--
-- Name: extras_exporttemplate; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE extras_exporttemplate (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    template_code text NOT NULL,
    mime_type character varying(15) NOT NULL,
    file_extension character varying(15) NOT NULL,
    content_type_id integer NOT NULL,
    description character varying(200) NOT NULL
);


ALTER TABLE extras_exporttemplate OWNER TO netbox;

--
-- Name: extras_exporttemplate_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE extras_exporttemplate_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE extras_exporttemplate_id_seq OWNER TO netbox;

--
-- Name: extras_exporttemplate_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE extras_exporttemplate_id_seq OWNED BY extras_exporttemplate.id;


--
-- Name: extras_graph; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE extras_graph (
    id integer NOT NULL,
    type smallint NOT NULL,
    weight smallint NOT NULL,
    name character varying(100) NOT NULL,
    source character varying(500) NOT NULL,
    link character varying(200) NOT NULL,
    CONSTRAINT extras_graph_type_check CHECK ((type >= 0)),
    CONSTRAINT extras_graph_weight_check CHECK ((weight >= 0))
);


ALTER TABLE extras_graph OWNER TO netbox;

--
-- Name: extras_graph_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE extras_graph_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE extras_graph_id_seq OWNER TO netbox;

--
-- Name: extras_graph_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE extras_graph_id_seq OWNED BY extras_graph.id;


--
-- Name: extras_imageattachment; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE extras_imageattachment (
    id integer NOT NULL,
    object_id integer NOT NULL,
    image character varying(100) NOT NULL,
    image_height smallint NOT NULL,
    image_width smallint NOT NULL,
    name character varying(50) NOT NULL,
    created timestamp with time zone NOT NULL,
    content_type_id integer NOT NULL,
    CONSTRAINT extras_imageattachment_image_height_check CHECK ((image_height >= 0)),
    CONSTRAINT extras_imageattachment_image_width_check CHECK ((image_width >= 0)),
    CONSTRAINT extras_imageattachment_object_id_check CHECK ((object_id >= 0))
);


ALTER TABLE extras_imageattachment OWNER TO netbox;

--
-- Name: extras_imageattachment_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE extras_imageattachment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE extras_imageattachment_id_seq OWNER TO netbox;

--
-- Name: extras_imageattachment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE extras_imageattachment_id_seq OWNED BY extras_imageattachment.id;


--
-- Name: extras_topologymap; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE extras_topologymap (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    slug character varying(50) NOT NULL,
    device_patterns text NOT NULL,
    description character varying(100) NOT NULL,
    site_id integer
);


ALTER TABLE extras_topologymap OWNER TO netbox;

--
-- Name: extras_topologymap_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE extras_topologymap_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE extras_topologymap_id_seq OWNER TO netbox;

--
-- Name: extras_topologymap_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE extras_topologymap_id_seq OWNED BY extras_topologymap.id;


--
-- Name: extras_useraction; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE extras_useraction (
    id integer NOT NULL,
    "time" timestamp with time zone NOT NULL,
    object_id integer,
    action smallint NOT NULL,
    message text NOT NULL,
    content_type_id integer NOT NULL,
    user_id integer NOT NULL,
    CONSTRAINT extras_useraction_action_check CHECK ((action >= 0)),
    CONSTRAINT extras_useraction_object_id_check CHECK ((object_id >= 0))
);


ALTER TABLE extras_useraction OWNER TO netbox;

--
-- Name: extras_useraction_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE extras_useraction_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE extras_useraction_id_seq OWNER TO netbox;

--
-- Name: extras_useraction_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE extras_useraction_id_seq OWNED BY extras_useraction.id;


--
-- Name: ipam_aggregate; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE ipam_aggregate (
    id integer NOT NULL,
    created date NOT NULL,
    last_updated timestamp with time zone NOT NULL,
    family smallint NOT NULL,
    prefix cidr NOT NULL,
    date_added date,
    description character varying(100) NOT NULL,
    rir_id integer NOT NULL,
    CONSTRAINT ipam_aggregate_family_check CHECK ((family >= 0))
);


ALTER TABLE ipam_aggregate OWNER TO netbox;

--
-- Name: ipam_aggregate_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE ipam_aggregate_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ipam_aggregate_id_seq OWNER TO netbox;

--
-- Name: ipam_aggregate_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE ipam_aggregate_id_seq OWNED BY ipam_aggregate.id;


--
-- Name: ipam_ipaddress; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE ipam_ipaddress (
    id integer NOT NULL,
    created date NOT NULL,
    last_updated timestamp with time zone NOT NULL,
    family smallint NOT NULL,
    address inet NOT NULL,
    description character varying(100) NOT NULL,
    interface_id integer,
    nat_inside_id integer,
    vrf_id integer,
    tenant_id integer,
    status smallint NOT NULL,
    CONSTRAINT ipam_ipaddress_family_check CHECK ((family >= 0)),
    CONSTRAINT ipam_ipaddress_status_check CHECK ((status >= 0))
);


ALTER TABLE ipam_ipaddress OWNER TO netbox;

--
-- Name: ipam_ipaddress_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE ipam_ipaddress_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ipam_ipaddress_id_seq OWNER TO netbox;

--
-- Name: ipam_ipaddress_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE ipam_ipaddress_id_seq OWNED BY ipam_ipaddress.id;


--
-- Name: ipam_prefix; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE ipam_prefix (
    id integer NOT NULL,
    created date NOT NULL,
    last_updated timestamp with time zone NOT NULL,
    family smallint NOT NULL,
    prefix cidr NOT NULL,
    status smallint NOT NULL,
    description character varying(100) NOT NULL,
    role_id integer,
    site_id integer,
    vlan_id integer,
    vrf_id integer,
    tenant_id integer,
    is_pool boolean NOT NULL,
    CONSTRAINT ipam_prefix_family_check CHECK ((family >= 0)),
    CONSTRAINT ipam_prefix_status_check CHECK ((status >= 0))
);


ALTER TABLE ipam_prefix OWNER TO netbox;

--
-- Name: ipam_prefix_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE ipam_prefix_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ipam_prefix_id_seq OWNER TO netbox;

--
-- Name: ipam_prefix_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE ipam_prefix_id_seq OWNED BY ipam_prefix.id;


--
-- Name: ipam_rir; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE ipam_rir (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    slug character varying(50) NOT NULL,
    is_private boolean NOT NULL
);


ALTER TABLE ipam_rir OWNER TO netbox;

--
-- Name: ipam_rir_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE ipam_rir_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ipam_rir_id_seq OWNER TO netbox;

--
-- Name: ipam_rir_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE ipam_rir_id_seq OWNED BY ipam_rir.id;


--
-- Name: ipam_role; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE ipam_role (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    slug character varying(50) NOT NULL,
    weight smallint NOT NULL,
    CONSTRAINT ipam_role_weight_check CHECK ((weight >= 0))
);


ALTER TABLE ipam_role OWNER TO netbox;

--
-- Name: ipam_role_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE ipam_role_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ipam_role_id_seq OWNER TO netbox;

--
-- Name: ipam_role_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE ipam_role_id_seq OWNED BY ipam_role.id;


--
-- Name: ipam_service; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE ipam_service (
    id integer NOT NULL,
    created date NOT NULL,
    last_updated timestamp with time zone NOT NULL,
    name character varying(30) NOT NULL,
    protocol smallint NOT NULL,
    port integer NOT NULL,
    description character varying(100) NOT NULL,
    device_id integer NOT NULL,
    CONSTRAINT ipam_service_port_check CHECK ((port >= 0)),
    CONSTRAINT ipam_service_protocol_check CHECK ((protocol >= 0))
);


ALTER TABLE ipam_service OWNER TO netbox;

--
-- Name: ipam_service_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE ipam_service_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ipam_service_id_seq OWNER TO netbox;

--
-- Name: ipam_service_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE ipam_service_id_seq OWNED BY ipam_service.id;


--
-- Name: ipam_service_ipaddresses; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE ipam_service_ipaddresses (
    id integer NOT NULL,
    service_id integer NOT NULL,
    ipaddress_id integer NOT NULL
);


ALTER TABLE ipam_service_ipaddresses OWNER TO netbox;

--
-- Name: ipam_service_ipaddresses_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE ipam_service_ipaddresses_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ipam_service_ipaddresses_id_seq OWNER TO netbox;

--
-- Name: ipam_service_ipaddresses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE ipam_service_ipaddresses_id_seq OWNED BY ipam_service_ipaddresses.id;


--
-- Name: ipam_vlan; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE ipam_vlan (
    id integer NOT NULL,
    created date NOT NULL,
    last_updated timestamp with time zone NOT NULL,
    vid smallint NOT NULL,
    name character varying(64) NOT NULL,
    status smallint NOT NULL,
    role_id integer,
    site_id integer,
    group_id integer,
    description character varying(100) NOT NULL,
    tenant_id integer,
    CONSTRAINT ipam_vlan_status_check CHECK ((status >= 0)),
    CONSTRAINT ipam_vlan_vid_check CHECK ((vid >= 0))
);


ALTER TABLE ipam_vlan OWNER TO netbox;

--
-- Name: ipam_vlan_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE ipam_vlan_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ipam_vlan_id_seq OWNER TO netbox;

--
-- Name: ipam_vlan_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE ipam_vlan_id_seq OWNED BY ipam_vlan.id;


--
-- Name: ipam_vlangroup; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE ipam_vlangroup (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    slug character varying(50) NOT NULL,
    site_id integer
);


ALTER TABLE ipam_vlangroup OWNER TO netbox;

--
-- Name: ipam_vlangroup_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE ipam_vlangroup_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ipam_vlangroup_id_seq OWNER TO netbox;

--
-- Name: ipam_vlangroup_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE ipam_vlangroup_id_seq OWNED BY ipam_vlangroup.id;


--
-- Name: ipam_vrf; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE ipam_vrf (
    id integer NOT NULL,
    created date NOT NULL,
    last_updated timestamp with time zone NOT NULL,
    name character varying(50) NOT NULL,
    rd character varying(21) NOT NULL,
    description character varying(100) NOT NULL,
    enforce_unique boolean NOT NULL,
    tenant_id integer
);


ALTER TABLE ipam_vrf OWNER TO netbox;

--
-- Name: ipam_vrf_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE ipam_vrf_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ipam_vrf_id_seq OWNER TO netbox;

--
-- Name: ipam_vrf_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE ipam_vrf_id_seq OWNED BY ipam_vrf.id;


--
-- Name: secrets_secret; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE secrets_secret (
    id integer NOT NULL,
    created date NOT NULL,
    last_updated timestamp with time zone NOT NULL,
    name character varying(100) NOT NULL,
    ciphertext bytea NOT NULL,
    hash character varying(128) NOT NULL,
    device_id integer NOT NULL,
    role_id integer NOT NULL
);


ALTER TABLE secrets_secret OWNER TO netbox;

--
-- Name: secrets_secret_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE secrets_secret_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE secrets_secret_id_seq OWNER TO netbox;

--
-- Name: secrets_secret_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE secrets_secret_id_seq OWNED BY secrets_secret.id;


--
-- Name: secrets_secretrole; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE secrets_secretrole (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    slug character varying(50) NOT NULL
);


ALTER TABLE secrets_secretrole OWNER TO netbox;

--
-- Name: secrets_secretrole_groups; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE secrets_secretrole_groups (
    id integer NOT NULL,
    secretrole_id integer NOT NULL,
    group_id integer NOT NULL
);


ALTER TABLE secrets_secretrole_groups OWNER TO netbox;

--
-- Name: secrets_secretrole_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE secrets_secretrole_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE secrets_secretrole_groups_id_seq OWNER TO netbox;

--
-- Name: secrets_secretrole_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE secrets_secretrole_groups_id_seq OWNED BY secrets_secretrole_groups.id;


--
-- Name: secrets_secretrole_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE secrets_secretrole_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE secrets_secretrole_id_seq OWNER TO netbox;

--
-- Name: secrets_secretrole_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE secrets_secretrole_id_seq OWNED BY secrets_secretrole.id;


--
-- Name: secrets_secretrole_users; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE secrets_secretrole_users (
    id integer NOT NULL,
    secretrole_id integer NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE secrets_secretrole_users OWNER TO netbox;

--
-- Name: secrets_secretrole_users_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE secrets_secretrole_users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE secrets_secretrole_users_id_seq OWNER TO netbox;

--
-- Name: secrets_secretrole_users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE secrets_secretrole_users_id_seq OWNED BY secrets_secretrole_users.id;


--
-- Name: secrets_sessionkey; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE secrets_sessionkey (
    id integer NOT NULL,
    cipher bytea NOT NULL,
    hash character varying(128) NOT NULL,
    created timestamp with time zone NOT NULL,
    userkey_id integer NOT NULL
);


ALTER TABLE secrets_sessionkey OWNER TO netbox;

--
-- Name: secrets_sessionkey_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE secrets_sessionkey_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE secrets_sessionkey_id_seq OWNER TO netbox;

--
-- Name: secrets_sessionkey_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE secrets_sessionkey_id_seq OWNED BY secrets_sessionkey.id;


--
-- Name: secrets_userkey; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE secrets_userkey (
    id integer NOT NULL,
    created date NOT NULL,
    last_updated timestamp with time zone NOT NULL,
    public_key text NOT NULL,
    master_key_cipher bytea,
    user_id integer NOT NULL
);


ALTER TABLE secrets_userkey OWNER TO netbox;

--
-- Name: secrets_userkey_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE secrets_userkey_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE secrets_userkey_id_seq OWNER TO netbox;

--
-- Name: secrets_userkey_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE secrets_userkey_id_seq OWNED BY secrets_userkey.id;


--
-- Name: tenancy_tenant; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE tenancy_tenant (
    id integer NOT NULL,
    created date NOT NULL,
    last_updated timestamp with time zone NOT NULL,
    name character varying(30) NOT NULL,
    slug character varying(50) NOT NULL,
    description character varying(100) NOT NULL,
    comments text NOT NULL,
    group_id integer
);


ALTER TABLE tenancy_tenant OWNER TO netbox;

--
-- Name: tenancy_tenant_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE tenancy_tenant_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE tenancy_tenant_id_seq OWNER TO netbox;

--
-- Name: tenancy_tenant_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE tenancy_tenant_id_seq OWNED BY tenancy_tenant.id;


--
-- Name: tenancy_tenantgroup; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE tenancy_tenantgroup (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    slug character varying(50) NOT NULL
);


ALTER TABLE tenancy_tenantgroup OWNER TO netbox;

--
-- Name: tenancy_tenantgroup_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE tenancy_tenantgroup_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE tenancy_tenantgroup_id_seq OWNER TO netbox;

--
-- Name: tenancy_tenantgroup_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE tenancy_tenantgroup_id_seq OWNED BY tenancy_tenantgroup.id;


--
-- Name: users_token; Type: TABLE; Schema: public; Owner: netbox
--

CREATE TABLE users_token (
    id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    expires timestamp with time zone,
    key character varying(40) NOT NULL,
    write_enabled boolean NOT NULL,
    description character varying(100) NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE users_token OWNER TO netbox;

--
-- Name: users_token_id_seq; Type: SEQUENCE; Schema: public; Owner: netbox
--

CREATE SEQUENCE users_token_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE users_token_id_seq OWNER TO netbox;

--
-- Name: users_token_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: netbox
--

ALTER SEQUENCE users_token_id_seq OWNED BY users_token.id;


--
-- Name: auth_group id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY auth_group ALTER COLUMN id SET DEFAULT nextval('auth_group_id_seq'::regclass);


--
-- Name: auth_group_permissions id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('auth_group_permissions_id_seq'::regclass);


--
-- Name: auth_permission id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY auth_permission ALTER COLUMN id SET DEFAULT nextval('auth_permission_id_seq'::regclass);


--
-- Name: auth_user id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY auth_user ALTER COLUMN id SET DEFAULT nextval('auth_user_id_seq'::regclass);


--
-- Name: auth_user_groups id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY auth_user_groups ALTER COLUMN id SET DEFAULT nextval('auth_user_groups_id_seq'::regclass);


--
-- Name: auth_user_user_permissions id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY auth_user_user_permissions ALTER COLUMN id SET DEFAULT nextval('auth_user_user_permissions_id_seq'::regclass);


--
-- Name: circuits_circuit id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY circuits_circuit ALTER COLUMN id SET DEFAULT nextval('circuits_circuit_id_seq'::regclass);


--
-- Name: circuits_circuittermination id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY circuits_circuittermination ALTER COLUMN id SET DEFAULT nextval('circuits_circuittermination_id_seq'::regclass);


--
-- Name: circuits_circuittype id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY circuits_circuittype ALTER COLUMN id SET DEFAULT nextval('circuits_circuittype_id_seq'::regclass);


--
-- Name: circuits_provider id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY circuits_provider ALTER COLUMN id SET DEFAULT nextval('circuits_provider_id_seq'::regclass);


--
-- Name: dcim_consoleport id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_consoleport ALTER COLUMN id SET DEFAULT nextval('dcim_consoleport_id_seq'::regclass);


--
-- Name: dcim_consoleporttemplate id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_consoleporttemplate ALTER COLUMN id SET DEFAULT nextval('dcim_consoleporttemplate_id_seq'::regclass);


--
-- Name: dcim_consoleserverport id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_consoleserverport ALTER COLUMN id SET DEFAULT nextval('dcim_consoleserverport_id_seq'::regclass);


--
-- Name: dcim_consoleserverporttemplate id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_consoleserverporttemplate ALTER COLUMN id SET DEFAULT nextval('dcim_consoleserverporttemplate_id_seq'::regclass);


--
-- Name: dcim_device id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_device ALTER COLUMN id SET DEFAULT nextval('dcim_device_id_seq'::regclass);


--
-- Name: dcim_devicebay id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_devicebay ALTER COLUMN id SET DEFAULT nextval('dcim_devicebay_id_seq'::regclass);


--
-- Name: dcim_devicebaytemplate id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_devicebaytemplate ALTER COLUMN id SET DEFAULT nextval('dcim_devicebaytemplate_id_seq'::regclass);


--
-- Name: dcim_devicerole id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_devicerole ALTER COLUMN id SET DEFAULT nextval('dcim_devicerole_id_seq'::regclass);


--
-- Name: dcim_devicetype id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_devicetype ALTER COLUMN id SET DEFAULT nextval('dcim_devicetype_id_seq'::regclass);


--
-- Name: dcim_interface id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_interface ALTER COLUMN id SET DEFAULT nextval('dcim_interface_id_seq'::regclass);


--
-- Name: dcim_interfaceconnection id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_interfaceconnection ALTER COLUMN id SET DEFAULT nextval('dcim_interfaceconnection_id_seq'::regclass);


--
-- Name: dcim_interfacetemplate id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_interfacetemplate ALTER COLUMN id SET DEFAULT nextval('dcim_interfacetemplate_id_seq'::regclass);


--
-- Name: dcim_inventoryitem id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_inventoryitem ALTER COLUMN id SET DEFAULT nextval('dcim_module_id_seq'::regclass);


--
-- Name: dcim_manufacturer id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_manufacturer ALTER COLUMN id SET DEFAULT nextval('dcim_manufacturer_id_seq'::regclass);


--
-- Name: dcim_platform id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_platform ALTER COLUMN id SET DEFAULT nextval('dcim_platform_id_seq'::regclass);


--
-- Name: dcim_poweroutlet id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_poweroutlet ALTER COLUMN id SET DEFAULT nextval('dcim_poweroutlet_id_seq'::regclass);


--
-- Name: dcim_poweroutlettemplate id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_poweroutlettemplate ALTER COLUMN id SET DEFAULT nextval('dcim_poweroutlettemplate_id_seq'::regclass);


--
-- Name: dcim_powerport id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_powerport ALTER COLUMN id SET DEFAULT nextval('dcim_powerport_id_seq'::regclass);


--
-- Name: dcim_powerporttemplate id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_powerporttemplate ALTER COLUMN id SET DEFAULT nextval('dcim_powerporttemplate_id_seq'::regclass);


--
-- Name: dcim_rack id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_rack ALTER COLUMN id SET DEFAULT nextval('dcim_rack_id_seq'::regclass);


--
-- Name: dcim_rackgroup id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_rackgroup ALTER COLUMN id SET DEFAULT nextval('dcim_rackgroup_id_seq'::regclass);


--
-- Name: dcim_rackreservation id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_rackreservation ALTER COLUMN id SET DEFAULT nextval('dcim_rackreservation_id_seq'::regclass);


--
-- Name: dcim_rackrole id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_rackrole ALTER COLUMN id SET DEFAULT nextval('dcim_rackrole_id_seq'::regclass);


--
-- Name: dcim_region id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_region ALTER COLUMN id SET DEFAULT nextval('dcim_region_id_seq'::regclass);


--
-- Name: dcim_site id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_site ALTER COLUMN id SET DEFAULT nextval('dcim_site_id_seq'::regclass);


--
-- Name: django_admin_log id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY django_admin_log ALTER COLUMN id SET DEFAULT nextval('django_admin_log_id_seq'::regclass);


--
-- Name: django_content_type id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY django_content_type ALTER COLUMN id SET DEFAULT nextval('django_content_type_id_seq'::regclass);


--
-- Name: django_migrations id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY django_migrations ALTER COLUMN id SET DEFAULT nextval('django_migrations_id_seq'::regclass);


--
-- Name: extras_customfield id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY extras_customfield ALTER COLUMN id SET DEFAULT nextval('extras_customfield_id_seq'::regclass);


--
-- Name: extras_customfield_obj_type id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY extras_customfield_obj_type ALTER COLUMN id SET DEFAULT nextval('extras_customfield_obj_type_id_seq'::regclass);


--
-- Name: extras_customfieldchoice id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY extras_customfieldchoice ALTER COLUMN id SET DEFAULT nextval('extras_customfieldchoice_id_seq'::regclass);


--
-- Name: extras_customfieldvalue id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY extras_customfieldvalue ALTER COLUMN id SET DEFAULT nextval('extras_customfieldvalue_id_seq'::regclass);


--
-- Name: extras_exporttemplate id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY extras_exporttemplate ALTER COLUMN id SET DEFAULT nextval('extras_exporttemplate_id_seq'::regclass);


--
-- Name: extras_graph id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY extras_graph ALTER COLUMN id SET DEFAULT nextval('extras_graph_id_seq'::regclass);


--
-- Name: extras_imageattachment id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY extras_imageattachment ALTER COLUMN id SET DEFAULT nextval('extras_imageattachment_id_seq'::regclass);


--
-- Name: extras_topologymap id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY extras_topologymap ALTER COLUMN id SET DEFAULT nextval('extras_topologymap_id_seq'::regclass);


--
-- Name: extras_useraction id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY extras_useraction ALTER COLUMN id SET DEFAULT nextval('extras_useraction_id_seq'::regclass);


--
-- Name: ipam_aggregate id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_aggregate ALTER COLUMN id SET DEFAULT nextval('ipam_aggregate_id_seq'::regclass);


--
-- Name: ipam_ipaddress id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_ipaddress ALTER COLUMN id SET DEFAULT nextval('ipam_ipaddress_id_seq'::regclass);


--
-- Name: ipam_prefix id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_prefix ALTER COLUMN id SET DEFAULT nextval('ipam_prefix_id_seq'::regclass);


--
-- Name: ipam_rir id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_rir ALTER COLUMN id SET DEFAULT nextval('ipam_rir_id_seq'::regclass);


--
-- Name: ipam_role id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_role ALTER COLUMN id SET DEFAULT nextval('ipam_role_id_seq'::regclass);


--
-- Name: ipam_service id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_service ALTER COLUMN id SET DEFAULT nextval('ipam_service_id_seq'::regclass);


--
-- Name: ipam_service_ipaddresses id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_service_ipaddresses ALTER COLUMN id SET DEFAULT nextval('ipam_service_ipaddresses_id_seq'::regclass);


--
-- Name: ipam_vlan id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_vlan ALTER COLUMN id SET DEFAULT nextval('ipam_vlan_id_seq'::regclass);


--
-- Name: ipam_vlangroup id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_vlangroup ALTER COLUMN id SET DEFAULT nextval('ipam_vlangroup_id_seq'::regclass);


--
-- Name: ipam_vrf id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_vrf ALTER COLUMN id SET DEFAULT nextval('ipam_vrf_id_seq'::regclass);


--
-- Name: secrets_secret id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY secrets_secret ALTER COLUMN id SET DEFAULT nextval('secrets_secret_id_seq'::regclass);


--
-- Name: secrets_secretrole id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY secrets_secretrole ALTER COLUMN id SET DEFAULT nextval('secrets_secretrole_id_seq'::regclass);


--
-- Name: secrets_secretrole_groups id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY secrets_secretrole_groups ALTER COLUMN id SET DEFAULT nextval('secrets_secretrole_groups_id_seq'::regclass);


--
-- Name: secrets_secretrole_users id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY secrets_secretrole_users ALTER COLUMN id SET DEFAULT nextval('secrets_secretrole_users_id_seq'::regclass);


--
-- Name: secrets_sessionkey id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY secrets_sessionkey ALTER COLUMN id SET DEFAULT nextval('secrets_sessionkey_id_seq'::regclass);


--
-- Name: secrets_userkey id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY secrets_userkey ALTER COLUMN id SET DEFAULT nextval('secrets_userkey_id_seq'::regclass);


--
-- Name: tenancy_tenant id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY tenancy_tenant ALTER COLUMN id SET DEFAULT nextval('tenancy_tenant_id_seq'::regclass);


--
-- Name: tenancy_tenantgroup id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY tenancy_tenantgroup ALTER COLUMN id SET DEFAULT nextval('tenancy_tenantgroup_id_seq'::regclass);


--
-- Name: users_token id; Type: DEFAULT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY users_token ALTER COLUMN id SET DEFAULT nextval('users_token_id_seq'::regclass);


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY auth_group (id, name) FROM stdin;
\.


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('auth_group_id_seq', 1, false);


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('auth_group_permissions_id_seq', 1, false);


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add log entry	1	add_logentry
2	Can change log entry	1	change_logentry
3	Can delete log entry	1	delete_logentry
4	Can add group	2	add_group
5	Can change group	2	change_group
6	Can delete group	2	delete_group
7	Can add permission	3	add_permission
8	Can change permission	3	change_permission
9	Can delete permission	3	delete_permission
10	Can add user	4	add_user
11	Can change user	4	change_user
12	Can delete user	4	delete_user
13	Can add content type	5	add_contenttype
14	Can change content type	5	change_contenttype
15	Can delete content type	5	delete_contenttype
16	Can add session	6	add_session
17	Can change session	6	change_session
18	Can delete session	6	delete_session
19	Can add provider	7	add_provider
20	Can change provider	7	change_provider
21	Can delete provider	7	delete_provider
22	Can add circuit termination	8	add_circuittermination
23	Can change circuit termination	8	change_circuittermination
24	Can delete circuit termination	8	delete_circuittermination
25	Can add circuit type	9	add_circuittype
26	Can change circuit type	9	change_circuittype
27	Can delete circuit type	9	delete_circuittype
28	Can add circuit	10	add_circuit
29	Can change circuit	10	change_circuit
30	Can delete circuit	10	delete_circuit
31	Can add device bay template	11	add_devicebaytemplate
32	Can change device bay template	11	change_devicebaytemplate
33	Can delete device bay template	11	delete_devicebaytemplate
34	Can add device bay	12	add_devicebay
35	Can change device bay	12	change_devicebay
36	Can delete device bay	12	delete_devicebay
37	Can add platform	13	add_platform
38	Can change platform	13	change_platform
39	Can delete platform	13	delete_platform
40	Can add rack role	14	add_rackrole
41	Can change rack role	14	change_rackrole
42	Can delete rack role	14	delete_rackrole
43	Can add interface	15	add_interface
44	Can change interface	15	change_interface
45	Can delete interface	15	delete_interface
46	Can add power port template	16	add_powerporttemplate
47	Can change power port template	16	change_powerporttemplate
48	Can delete power port template	16	delete_powerporttemplate
49	Can add console server port	17	add_consoleserverport
50	Can change console server port	17	change_consoleserverport
51	Can delete console server port	17	delete_consoleserverport
52	Can add site	18	add_site
53	Can change site	18	change_site
54	Can delete site	18	delete_site
55	Can add device	19	add_device
56	Can change device	19	change_device
57	Can delete device	19	delete_device
58	Can add rack	20	add_rack
59	Can change rack	20	change_rack
60	Can delete rack	20	delete_rack
61	Can add power port	21	add_powerport
62	Can change power port	21	change_powerport
63	Can delete power port	21	delete_powerport
64	Can add interface template	22	add_interfacetemplate
65	Can change interface template	22	change_interfacetemplate
66	Can delete interface template	22	delete_interfacetemplate
67	Can add console port template	23	add_consoleporttemplate
68	Can change console port template	23	change_consoleporttemplate
69	Can delete console port template	23	delete_consoleporttemplate
70	Can add device role	24	add_devicerole
71	Can change device role	24	change_devicerole
72	Can delete device role	24	delete_devicerole
73	Can add rack group	25	add_rackgroup
74	Can change rack group	25	change_rackgroup
75	Can delete rack group	25	delete_rackgroup
76	Can add rack reservation	26	add_rackreservation
77	Can change rack reservation	26	change_rackreservation
78	Can delete rack reservation	26	delete_rackreservation
79	Can add interface connection	27	add_interfaceconnection
80	Can change interface connection	27	change_interfaceconnection
81	Can delete interface connection	27	delete_interfaceconnection
82	Can add inventory item	28	add_inventoryitem
83	Can change inventory item	28	change_inventoryitem
84	Can delete inventory item	28	delete_inventoryitem
85	Can add manufacturer	29	add_manufacturer
86	Can change manufacturer	29	change_manufacturer
87	Can delete manufacturer	29	delete_manufacturer
88	Can add region	30	add_region
89	Can change region	30	change_region
90	Can delete region	30	delete_region
91	Can add console port	31	add_consoleport
92	Can change console port	31	change_consoleport
93	Can delete console port	31	delete_consoleport
94	Can add console server port template	32	add_consoleserverporttemplate
95	Can change console server port template	32	change_consoleserverporttemplate
96	Can delete console server port template	32	delete_consoleserverporttemplate
97	Can add power outlet	33	add_poweroutlet
98	Can change power outlet	33	change_poweroutlet
99	Can delete power outlet	33	delete_poweroutlet
100	Can add device type	34	add_devicetype
101	Can change device type	34	change_devicetype
102	Can delete device type	34	delete_devicetype
103	Can add power outlet template	35	add_poweroutlettemplate
104	Can change power outlet template	35	change_poweroutlettemplate
105	Can delete power outlet template	35	delete_poweroutlettemplate
106	Can add role	36	add_role
107	Can change role	36	change_role
108	Can delete role	36	delete_role
109	Can add service	37	add_service
110	Can change service	37	change_service
111	Can delete service	37	delete_service
112	Can add VLAN group	38	add_vlangroup
113	Can change VLAN group	38	change_vlangroup
114	Can delete VLAN group	38	delete_vlangroup
115	Can add VRF	39	add_vrf
116	Can change VRF	39	change_vrf
117	Can delete VRF	39	delete_vrf
118	Can add IP address	40	add_ipaddress
119	Can change IP address	40	change_ipaddress
120	Can delete IP address	40	delete_ipaddress
121	Can add aggregate	41	add_aggregate
122	Can change aggregate	41	change_aggregate
123	Can delete aggregate	41	delete_aggregate
124	Can add RIR	42	add_rir
125	Can change RIR	42	change_rir
126	Can delete RIR	42	delete_rir
127	Can add VLAN	43	add_vlan
128	Can change VLAN	43	change_vlan
129	Can delete VLAN	43	delete_vlan
130	Can add prefix	44	add_prefix
131	Can change prefix	44	change_prefix
132	Can delete prefix	44	delete_prefix
133	Can add custom field	45	add_customfield
134	Can change custom field	45	change_customfield
135	Can delete custom field	45	delete_customfield
136	Can add user action	46	add_useraction
137	Can change user action	46	change_useraction
138	Can delete user action	46	delete_useraction
139	Can add graph	47	add_graph
140	Can change graph	47	change_graph
141	Can delete graph	47	delete_graph
142	Can add export template	48	add_exporttemplate
143	Can change export template	48	change_exporttemplate
144	Can delete export template	48	delete_exporttemplate
145	Can add custom field choice	49	add_customfieldchoice
146	Can change custom field choice	49	change_customfieldchoice
147	Can delete custom field choice	49	delete_customfieldchoice
148	Can add topology map	50	add_topologymap
149	Can change topology map	50	change_topologymap
150	Can delete topology map	50	delete_topologymap
151	Can add custom field value	51	add_customfieldvalue
152	Can change custom field value	51	change_customfieldvalue
153	Can delete custom field value	51	delete_customfieldvalue
154	Can add secret	52	add_secret
155	Can change secret	52	change_secret
156	Can delete secret	52	delete_secret
157	Can add user key	53	add_userkey
158	Can change user key	53	change_userkey
159	Can delete user key	53	delete_userkey
160	Can activate user keys for decryption	53	activate_userkey
161	Can add secret role	54	add_secretrole
162	Can change secret role	54	change_secretrole
163	Can delete secret role	54	delete_secretrole
164	Can add session key	55	add_sessionkey
165	Can change session key	55	change_sessionkey
166	Can delete session key	55	delete_sessionkey
167	Can add tenant group	56	add_tenantgroup
168	Can change tenant group	56	change_tenantgroup
169	Can delete tenant group	56	delete_tenantgroup
170	Can add tenant	57	add_tenant
171	Can change tenant	57	change_tenant
172	Can delete tenant	57	delete_tenant
173	Can add image attachment	59	add_imageattachment
174	Can change image attachment	59	change_imageattachment
175	Can delete image attachment	59	delete_imageattachment
\.


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('auth_permission_id_seq', 205, true);


--
-- Data for Name: auth_user; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) FROM stdin;
1	pbkdf2_sha256$36000$9xLV2SBc0idx$T2Wvku5Toy/yoPCcPTY+mnctebo5f0y5PClMwubTlqA=	2017-04-27 07:17:46.194597+00	t	admin			admin@example.com	t	t	2017-04-12 12:04:55.905911+00
\.


--
-- Data for Name: auth_user_groups; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY auth_user_groups (id, user_id, group_id) FROM stdin;
\.


--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('auth_user_groups_id_seq', 1, false);


--
-- Name: auth_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('auth_user_id_seq', 34, true);


--
-- Data for Name: auth_user_user_permissions; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY auth_user_user_permissions (id, user_id, permission_id) FROM stdin;
\.


--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('auth_user_user_permissions_id_seq', 1, false);


--
-- Data for Name: circuits_circuit; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY circuits_circuit (id, created, last_updated, cid, install_date, commit_rate, comments, provider_id, type_id, tenant_id, description) FROM stdin;
\.


--
-- Name: circuits_circuit_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('circuits_circuit_id_seq', 1, false);


--
-- Data for Name: circuits_circuittermination; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY circuits_circuittermination (id, term_side, port_speed, upstream_speed, xconnect_id, pp_info, circuit_id, interface_id, site_id) FROM stdin;
\.


--
-- Name: circuits_circuittermination_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('circuits_circuittermination_id_seq', 1, false);


--
-- Data for Name: circuits_circuittype; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY circuits_circuittype (id, name, slug) FROM stdin;
\.


--
-- Name: circuits_circuittype_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('circuits_circuittype_id_seq', 1, false);


--
-- Data for Name: circuits_provider; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY circuits_provider (id, created, last_updated, name, slug, asn, account, portal_url, noc_contact, admin_contact, comments) FROM stdin;
\.


--
-- Name: circuits_provider_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('circuits_provider_id_seq', 1, false);


--
-- Data for Name: dcim_consoleport; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY dcim_consoleport (id, name, connection_status, cs_port_id, device_id) FROM stdin;
\.


--
-- Name: dcim_consoleport_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('dcim_consoleport_id_seq', 1, false);


--
-- Data for Name: dcim_consoleporttemplate; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY dcim_consoleporttemplate (id, name, device_type_id) FROM stdin;
\.


--
-- Name: dcim_consoleporttemplate_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('dcim_consoleporttemplate_id_seq', 1, false);


--
-- Data for Name: dcim_consoleserverport; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY dcim_consoleserverport (id, name, device_id) FROM stdin;
\.


--
-- Name: dcim_consoleserverport_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('dcim_consoleserverport_id_seq', 1, false);


--
-- Data for Name: dcim_consoleserverporttemplate; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY dcim_consoleserverporttemplate (id, name, device_type_id) FROM stdin;
\.


--
-- Name: dcim_consoleserverporttemplate_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('dcim_consoleserverporttemplate_id_seq', 1, false);


--
-- Data for Name: dcim_device; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY dcim_device (id, created, last_updated, name, serial, "position", face, status, comments, device_role_id, device_type_id, platform_id, rack_id, primary_ip4_id, primary_ip6_id, tenant_id, asset_tag, site_id) FROM stdin;
3	2017-05-04	2017-05-04 08:51:34.497265+00	parent_device1		41	0	t		1	2	\N	1	\N	\N	\N	\N	2
4	2017-05-04	2017-05-04 08:51:56.350759+00	child_device1		\N	\N	t		1	3	\N	1	\N	\N	\N	\N	2
1	2017-04-13	2017-05-05 05:09:11.667237+00	device1		39	1	t	trewyutglibjwfvd	1	1	\N	1	\N	\N	\N	\N	2
2	2017-04-13	2017-05-05 06:15:12.972981+00	device2	123456	42	0	t		1	1	1	1	1	5	3	654321	2
\.


--
-- Name: dcim_device_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('dcim_device_id_seq', 4, true);


--
-- Data for Name: dcim_devicebay; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY dcim_devicebay (id, name, device_id, installed_device_id) FROM stdin;
\.


--
-- Name: dcim_devicebay_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('dcim_devicebay_id_seq', 1, false);


--
-- Data for Name: dcim_devicebaytemplate; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY dcim_devicebaytemplate (id, name, device_type_id) FROM stdin;
\.


--
-- Name: dcim_devicebaytemplate_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('dcim_devicebaytemplate_id_seq', 1, false);


--
-- Data for Name: dcim_devicerole; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY dcim_devicerole (id, name, slug, color) FROM stdin;
1	devicerole1	devicerole1	aa1409
\.


--
-- Name: dcim_devicerole_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('dcim_devicerole_id_seq', 1, true);


--
-- Data for Name: dcim_devicetype; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY dcim_devicetype (id, model, slug, u_height, is_full_depth, is_console_server, is_pdu, is_network_device, manufacturer_id, subdevice_role, part_number, comments, interface_ordering) FROM stdin;
1	devicetype1	devicetype1	1	t	f	f	t	1	\N			1
2	parent1	parent1	1	t	f	f	t	1	t			1
3	child1	child1	0	t	f	f	t	1	f			1
\.


--
-- Name: dcim_devicetype_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('dcim_devicetype_id_seq', 3, true);


--
-- Data for Name: dcim_interface; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY dcim_interface (id, name, form_factor, mgmt_only, description, device_id, mac_address, lag_id) FROM stdin;
1	e0	1000	f		1	\N	\N
3	interface2	200	f	lag1	2	\N	\N
2	interface1	1000	f	description of interface1	2	00:11:22:33:44:55	3
\.


--
-- Name: dcim_interface_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('dcim_interface_id_seq', 3, true);


--
-- Data for Name: dcim_interfaceconnection; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY dcim_interfaceconnection (id, connection_status, interface_a_id, interface_b_id) FROM stdin;
\.


--
-- Name: dcim_interfaceconnection_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('dcim_interfaceconnection_id_seq', 1, false);


--
-- Data for Name: dcim_interfacetemplate; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY dcim_interfacetemplate (id, name, form_factor, mgmt_only, device_type_id) FROM stdin;
\.


--
-- Name: dcim_interfacetemplate_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('dcim_interfacetemplate_id_seq', 1, false);


--
-- Data for Name: dcim_inventoryitem; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY dcim_inventoryitem (id, name, part_id, serial, discovered, device_id, parent_id, manufacturer_id) FROM stdin;
1	inventory_item1			f	1	\N	\N
2	Disk1			f	1	\N	\N
\.


--
-- Data for Name: dcim_manufacturer; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY dcim_manufacturer (id, name, slug) FROM stdin;
1	manu1	manu1
\.


--
-- Name: dcim_manufacturer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('dcim_manufacturer_id_seq', 1, true);


--
-- Name: dcim_module_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('dcim_module_id_seq', 2, true);


--
-- Data for Name: dcim_platform; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY dcim_platform (id, name, slug, rpc_client) FROM stdin;
1	platform1	platform1	
\.


--
-- Name: dcim_platform_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('dcim_platform_id_seq', 1, true);


--
-- Data for Name: dcim_poweroutlet; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY dcim_poweroutlet (id, name, device_id) FROM stdin;
\.


--
-- Name: dcim_poweroutlet_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('dcim_poweroutlet_id_seq', 1, false);


--
-- Data for Name: dcim_poweroutlettemplate; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY dcim_poweroutlettemplate (id, name, device_type_id) FROM stdin;
\.


--
-- Name: dcim_poweroutlettemplate_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('dcim_poweroutlettemplate_id_seq', 1, false);


--
-- Data for Name: dcim_powerport; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY dcim_powerport (id, name, connection_status, device_id, power_outlet_id) FROM stdin;
\.


--
-- Name: dcim_powerport_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('dcim_powerport_id_seq', 1, false);


--
-- Data for Name: dcim_powerporttemplate; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY dcim_powerporttemplate (id, name, device_type_id) FROM stdin;
\.


--
-- Name: dcim_powerporttemplate_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('dcim_powerporttemplate_id_seq', 1, false);


--
-- Data for Name: dcim_rack; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY dcim_rack (id, created, last_updated, name, facility_id, u_height, comments, group_id, site_id, tenant_id, type, width, role_id, desc_units) FROM stdin;
1	2017-04-13	2017-04-13 07:32:22.150682+00	test2rack	\N	42		\N	2	\N	\N	19	\N	f
\.


--
-- Name: dcim_rack_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('dcim_rack_id_seq', 1, true);


--
-- Data for Name: dcim_rackgroup; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY dcim_rackgroup (id, name, slug, site_id) FROM stdin;
\.


--
-- Name: dcim_rackgroup_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('dcim_rackgroup_id_seq', 1, false);


--
-- Data for Name: dcim_rackreservation; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY dcim_rackreservation (id, units, created, description, rack_id, user_id) FROM stdin;
\.


--
-- Name: dcim_rackreservation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('dcim_rackreservation_id_seq', 1, false);


--
-- Data for Name: dcim_rackrole; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY dcim_rackrole (id, name, slug, color) FROM stdin;
\.


--
-- Name: dcim_rackrole_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('dcim_rackrole_id_seq', 1, false);


--
-- Data for Name: dcim_region; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY dcim_region (id, name, slug, lft, rght, tree_id, level, parent_id) FROM stdin;
1	region1	region1	1	4	1	0	\N
2	sub_region1	sub_region1	2	3	1	1	1
\.


--
-- Name: dcim_region_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('dcim_region_id_seq', 2, true);


--
-- Data for Name: dcim_site; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY dcim_site (id, created, last_updated, name, slug, facility, asn, physical_address, shipping_address, comments, tenant_id, contact_email, contact_name, contact_phone, region_id) FROM stdin;
2	2017-04-13	2017-04-27 07:23:40.289324+00	test_site2	test2		\N				\N				\N
1	2017-04-12	2017-05-05 09:03:18.253899+00	new name	test		\N				\N				1
\.


--
-- Name: dcim_site_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('dcim_site_id_seq', 3, true);


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
1	2017-04-27 07:22:04.607442+00	1	Custom Field Text:	1	[{"added": {}}]	45	1
2	2017-04-27 07:22:47.298771+00	2	Int Custom Field	1	[{"added": {}}]	45	1
3	2017-04-27 07:23:14.589876+00	3	Boolean Custom Field	1	[{"added": {}}]	45	1
4	2017-05-02 08:55:32.74545+00	4	Custom1	1	[{"added": {}}]	45	1
\.


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('django_admin_log_id_seq', 4, true);


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY django_content_type (id, app_label, model) FROM stdin;
1	admin	logentry
2	auth	group
3	auth	permission
4	auth	user
5	contenttypes	contenttype
6	sessions	session
7	circuits	provider
8	circuits	circuittermination
9	circuits	circuittype
10	circuits	circuit
11	dcim	devicebaytemplate
12	dcim	devicebay
13	dcim	platform
14	dcim	rackrole
15	dcim	interface
16	dcim	powerporttemplate
17	dcim	consoleserverport
18	dcim	site
19	dcim	device
20	dcim	rack
21	dcim	powerport
22	dcim	interfacetemplate
23	dcim	consoleporttemplate
24	dcim	devicerole
25	dcim	rackgroup
26	dcim	rackreservation
27	dcim	interfaceconnection
28	dcim	inventoryitem
29	dcim	manufacturer
30	dcim	region
31	dcim	consoleport
32	dcim	consoleserverporttemplate
33	dcim	poweroutlet
34	dcim	devicetype
35	dcim	poweroutlettemplate
36	ipam	role
37	ipam	service
38	ipam	vlangroup
39	ipam	vrf
40	ipam	ipaddress
41	ipam	aggregate
42	ipam	rir
43	ipam	vlan
44	ipam	prefix
45	extras	customfield
46	extras	useraction
47	extras	graph
48	extras	exporttemplate
49	extras	customfieldchoice
50	extras	topologymap
51	extras	customfieldvalue
52	secrets	secret
53	secrets	userkey
54	secrets	secretrole
55	secrets	sessionkey
56	tenancy	tenantgroup
57	tenancy	tenant
58	users	token
59	extras	imageattachment
\.


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('django_content_type_id_seq', 91, true);


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY django_migrations (id, app, name, applied) FROM stdin;
1	contenttypes	0001_initial	2017-04-12 12:04:37.07475+00
2	auth	0001_initial	2017-04-12 12:04:37.648799+00
3	admin	0001_initial	2017-04-12 12:04:37.782964+00
4	admin	0002_logentry_remove_auto_add	2017-04-12 12:04:37.820335+00
5	contenttypes	0002_remove_content_type_name	2017-04-12 12:04:37.872229+00
6	auth	0002_alter_permission_name_max_length	2017-04-12 12:04:37.902909+00
7	auth	0003_alter_user_email_max_length	2017-04-12 12:04:37.942105+00
8	auth	0004_alter_user_username_opts	2017-04-12 12:04:37.967956+00
9	auth	0005_alter_user_last_login_null	2017-04-12 12:04:38.008801+00
10	auth	0006_require_contenttypes_0002	2017-04-12 12:04:38.022452+00
11	auth	0007_alter_validators_add_error_messages	2017-04-12 12:04:38.045587+00
12	auth	0008_alter_user_username_max_length	2017-04-12 12:04:38.103995+00
13	tenancy	0001_initial	2017-04-12 12:04:38.429227+00
14	dcim	0001_initial	2017-04-12 12:04:40.182601+00
15	ipam	0001_initial	2017-04-12 12:04:41.067993+00
16	dcim	0002_auto_20160622_1821	2017-04-12 12:04:42.185407+00
17	dcim	0003_auto_20160628_1721	2017-04-12 12:04:42.225813+00
18	dcim	0004_auto_20160701_2049	2017-04-12 12:04:42.5023+00
19	dcim	0005_auto_20160706_1722	2017-04-12 12:04:42.554332+00
20	dcim	0006_add_device_primary_ip4_ip6	2017-04-12 12:04:42.665025+00
21	dcim	0007_device_copy_primary_ip	2017-04-12 12:04:42.721591+00
22	dcim	0008_device_remove_primary_ip	2017-04-12 12:04:42.773239+00
23	dcim	0009_site_32bit_asn_support	2017-04-12 12:04:42.960971+00
24	dcim	0010_devicebay_installed_device_set_null	2017-04-12 12:04:43.012674+00
25	dcim	0011_devicetype_part_number	2017-04-12 12:04:43.202789+00
26	dcim	0012_site_rack_device_add_tenant	2017-04-12 12:04:43.365934+00
27	dcim	0013_add_interface_form_factors	2017-04-12 12:04:43.417916+00
28	dcim	0014_rack_add_type_width	2017-04-12 12:04:43.630815+00
29	dcim	0015_rack_add_u_height_validator	2017-04-12 12:04:43.658013+00
30	dcim	0016_module_add_manufacturer	2017-04-12 12:04:43.736362+00
31	dcim	0017_rack_add_role	2017-04-12 12:04:43.953567+00
32	dcim	0018_device_add_asset_tag	2017-04-12 12:04:44.052647+00
33	dcim	0019_new_iface_form_factors	2017-04-12 12:04:44.102866+00
34	dcim	0020_rack_desc_units	2017-04-12 12:04:44.340647+00
35	dcim	0021_add_ff_flexstack	2017-04-12 12:04:44.402867+00
36	dcim	0022_color_names_to_rgb	2017-04-12 12:04:44.872002+00
37	circuits	0001_initial	2017-04-12 12:04:45.227427+00
38	circuits	0002_auto_20160622_1821	2017-04-12 12:04:45.498514+00
39	circuits	0003_provider_32bit_asn_support	2017-04-12 12:04:45.680445+00
40	circuits	0004_circuit_add_tenant	2017-04-12 12:04:45.757384+00
41	circuits	0005_circuit_add_upstream_speed	2017-04-12 12:04:45.806022+00
42	circuits	0006_terminations	2017-04-12 12:04:46.201959+00
43	circuits	0007_circuit_add_description	2017-04-12 12:04:46.388024+00
44	dcim	0023_devicetype_comments	2017-04-12 12:04:46.615799+00
45	dcim	0024_site_add_contact_fields	2017-04-12 12:04:47.18374+00
46	dcim	0025_devicetype_add_interface_ordering	2017-04-12 12:04:47.381708+00
47	dcim	0026_add_rack_reservations	2017-04-12 12:04:47.537198+00
48	dcim	0027_device_add_site	2017-04-12 12:04:47.626324+00
49	dcim	0028_device_copy_rack_to_site	2017-04-12 12:04:47.696153+00
50	dcim	0029_allow_rackless_devices	2017-04-12 12:04:47.934782+00
51	dcim	0030_interface_add_lag	2017-04-12 12:04:48.05912+00
52	dcim	0031_regions	2017-04-12 12:04:48.376893+00
53	dcim	0032_device_increase_name_length	2017-04-12 12:04:48.433258+00
54	dcim	0033_rackreservation_rack_editable	2017-04-12 12:04:48.502781+00
55	dcim	0034_rename_module_to_inventoryitem	2017-04-12 12:04:48.706302+00
56	extras	0001_initial	2017-04-12 12:04:49.303691+00
57	extras	0002_custom_fields	2017-04-12 12:04:49.829688+00
58	extras	0003_exporttemplate_add_description	2017-04-12 12:04:50.195843+00
59	extras	0004_topologymap_change_comma_to_semicolon	2017-04-12 12:04:50.287746+00
60	ipam	0002_vrf_add_enforce_unique	2017-04-12 12:04:50.412995+00
61	ipam	0003_ipam_add_vlangroups	2017-04-12 12:04:50.695226+00
62	ipam	0004_ipam_vlangroup_uniqueness	2017-04-12 12:04:50.829439+00
63	ipam	0005_auto_20160725_1842	2017-04-12 12:04:51.065549+00
64	ipam	0006_vrf_vlan_add_tenant	2017-04-12 12:04:51.215487+00
65	ipam	0007_prefix_ipaddress_add_tenant	2017-04-12 12:04:51.361982+00
66	ipam	0008_prefix_change_order	2017-04-12 12:04:51.404663+00
67	ipam	0009_ipaddress_add_status	2017-04-12 12:04:51.588148+00
68	ipam	0010_ipaddress_help_texts	2017-04-12 12:04:51.678387+00
69	ipam	0011_rir_add_is_private	2017-04-12 12:04:51.851377+00
70	ipam	0012_services	2017-04-12 12:04:52.10719+00
71	ipam	0013_prefix_add_is_pool	2017-04-12 12:04:52.533382+00
72	ipam	0014_ipaddress_status_add_deprecated	2017-04-12 12:04:52.567422+00
73	ipam	0015_global_vlans	2017-04-12 12:04:52.674361+00
74	secrets	0001_initial	2017-04-12 12:04:53.446685+00
75	secrets	0002_userkey_add_session_key	2017-04-12 12:04:53.675611+00
76	sessions	0001_initial	2017-04-12 12:04:53.800133+00
77	tenancy	0002_tenant_group_optional	2017-04-12 12:04:53.909421+00
78	users	0001_api_tokens	2017-04-12 12:04:54.092337+00
79	extras	0005_useraction_add_bulk_create	2017-04-27 07:06:22.554162+00
80	extras	0006_add_imageattachments	2017-04-27 07:06:22.76895+00
\.


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('django_migrations_id_seq', 111, true);


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY django_session (session_key, session_data, expire_date) FROM stdin;
7t20aaqs6k739jymk6839hwzewuwjety	ZjYyOWZmMTkzOTBjYWFkNWQ5NWUwY2UzZDZhZWY3OWYzZWFhNGQzMzp7Il9hdXRoX3VzZXJfaGFzaCI6IjdhZjQ4M2M0MzJkZTRmNjZkM2QxM2MzZmRiYTAxZjJkMTZlM2RjZGMiLCJfYXV0aF91c2VyX2JhY2tlbmQiOiJkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZCIsIl9hdXRoX3VzZXJfaWQiOiIxIn0=	2017-04-26 12:06:17.711796+00
9yh3t1pef0qzmug5oh5hwb4fqw1g8jjr	ZjYyOWZmMTkzOTBjYWFkNWQ5NWUwY2UzZDZhZWY3OWYzZWFhNGQzMzp7Il9hdXRoX3VzZXJfaGFzaCI6IjdhZjQ4M2M0MzJkZTRmNjZkM2QxM2MzZmRiYTAxZjJkMTZlM2RjZGMiLCJfYXV0aF91c2VyX2JhY2tlbmQiOiJkamFuZ28uY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZCIsIl9hdXRoX3VzZXJfaWQiOiIxIn0=	2017-05-11 07:17:46.209544+00
\.


--
-- Data for Name: extras_customfield; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY extras_customfield (id, type, name, label, description, required, is_filterable, "default", weight) FROM stdin;
1	100	site_custom_field	Custom Field Text:		t	t		100
2	200	custom_field_int	Int Custom Field	Not required	f	t		100
3	300	custom_field_bool	Boolean Custom Field		f	t		100
4	100	custom1			f	t		100
\.


--
-- Name: extras_customfield_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('extras_customfield_id_seq', 4, true);


--
-- Data for Name: extras_customfield_obj_type; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY extras_customfield_obj_type (id, customfield_id, contenttype_id) FROM stdin;
1	1	18
2	2	18
3	3	18
4	4	19
\.


--
-- Name: extras_customfield_obj_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('extras_customfield_obj_type_id_seq', 4, true);


--
-- Data for Name: extras_customfieldchoice; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY extras_customfieldchoice (id, value, weight, field_id) FROM stdin;
\.


--
-- Name: extras_customfieldchoice_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('extras_customfieldchoice_id_seq', 1, false);


--
-- Data for Name: extras_customfieldvalue; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY extras_customfieldvalue (id, obj_id, serialized_value, field_id, obj_type_id) FROM stdin;
1	2	1	3	18
2	2	55	2	18
3	2	uuh	1	18
5	2	custom1	4	19
4	1	WICHTIG	4	19
\.


--
-- Name: extras_customfieldvalue_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('extras_customfieldvalue_id_seq', 5, true);


--
-- Data for Name: extras_exporttemplate; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY extras_exporttemplate (id, name, template_code, mime_type, file_extension, content_type_id, description) FROM stdin;
\.


--
-- Name: extras_exporttemplate_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('extras_exporttemplate_id_seq', 1, false);


--
-- Data for Name: extras_graph; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY extras_graph (id, type, weight, name, source, link) FROM stdin;
\.


--
-- Name: extras_graph_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('extras_graph_id_seq', 1, false);


--
-- Data for Name: extras_imageattachment; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY extras_imageattachment (id, object_id, image, image_height, image_width, name, created, content_type_id) FROM stdin;
\.


--
-- Name: extras_imageattachment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('extras_imageattachment_id_seq', 1, false);


--
-- Data for Name: extras_topologymap; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY extras_topologymap (id, name, slug, device_patterns, description, site_id) FROM stdin;
\.


--
-- Name: extras_topologymap_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('extras_topologymap_id_seq', 1, false);


--
-- Data for Name: extras_useraction; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY extras_useraction (id, "time", object_id, action, message, content_type_id, user_id) FROM stdin;
1	2017-04-12 12:06:27.378589+00	1	1	Created site <a href="/dcim/sites/test/">test</a>	18	1
2	2017-04-13 06:27:15.276909+00	2	1	Created site <a href="/dcim/sites/test2/">test2</a>	18	1
3	2017-04-13 07:30:34.131782+00	1	1	Created region <a href="/dcim/sites/?region=region1">region1</a>	30	1
4	2017-04-13 07:30:48.089344+00	1	3	Modified site <a href="/dcim/sites/test/">test</a>	18	1
5	2017-04-13 07:32:22.160552+00	1	1	Created rack <a href="/dcim/racks/1/">test2rack</a>	20	1
6	2017-04-13 07:35:09.68698+00	1	1	Created platform <a href="/dcim/devices/?platform=platform1">platform1</a>	13	1
7	2017-04-13 07:35:14.035837+00	1	1	Created manufacturer <a href="/dcim/device-types/?manufacturer=manu1">manu1</a>	29	1
8	2017-04-13 07:35:21.69209+00	1	1	Created device role <a href="/dcim/devices/?role=devicerole1">devicerole1</a>	24	1
9	2017-04-13 07:35:31.139203+00	1	1	Created device type <a href="/dcim/device-types/1/">devicetype1</a>	34	1
10	2017-04-13 07:35:46.769551+00	1	1	Created device <a href="/dcim/devices/1/">device1</a>	19	1
11	2017-04-13 07:36:19.026171+00	2	1	Created device <a href="/dcim/devices/2/">device2</a>	19	1
12	2017-04-13 11:42:26.916947+00	1	1	Created inventory item inventory_item1	28	1
13	2017-04-13 12:17:19.068981+00	2	3	Modified device <a href="/dcim/devices/2/">device2</a>	19	1
14	2017-04-27 07:23:40.358776+00	2	3	Modified site <a href="/dcim/sites/test2/">test_site2</a>	18	1
15	2017-04-27 08:35:52.132555+00	1	1	Created prefix <a href="/ipam/prefixes/1/">10.0.0.0/8</a>	44	1
16	2017-04-27 08:37:50.6315+00	1	1	Created IP address <a href="/ipam/ip-addresses/1/">10.0.0.1/8</a>	40	1
17	2017-05-02 08:43:02.828907+00	2	1	Created inventory item Disk1	28	1
18	2017-05-02 08:55:44.671624+00	1	3	Modified device <a href="/dcim/devices/1/">device1</a>	19	1
19	2017-05-02 09:06:54.795443+00	1	3	Modified device <a href="/dcim/devices/1/">device1</a>	19	1
20	2017-05-02 13:26:16.898551+00	2	1	Created region <a href="/dcim/sites/?region=sub_region1">sub_region1</a>	30	1
21	2017-05-02 14:46:44.027644+00	1	1	Created tenant <a href="/tenancy/tenants/tenant1/">tenant1</a>	57	1
22	2017-05-02 14:47:04.878812+00	1	1	Created tenant group <a href="/tenancy/tenants/?group=customer">Customer</a>	56	1
23	2017-05-02 14:47:18.943254+00	1	3	Modified tenant group <a href="/tenancy/tenants/?group=customer">Customer</a>	56	1
24	2017-05-02 14:47:28.728391+00	2	1	Created tenant <a href="/tenancy/tenants/tenant2/">tenant2</a>	57	1
25	2017-05-02 14:47:37.293332+00	3	1	Created tenant <a href="/tenancy/tenants/tenant3/">tenant3</a>	57	1
26	2017-05-02 16:15:40.15251+00	1	1	Created role role1	36	1
27	2017-05-02 16:15:48.016713+00	1	1	Created RIR <a href="/ipam/aggregates/?rir=rir1">rir1</a>	42	1
28	2017-05-02 16:15:54.362925+00	2	1	Created RIR <a href="/ipam/aggregates/?rir=rir2">rir2</a>	42	1
29	2017-05-02 16:16:15.115109+00	1	1	Created VRF <a href="/ipam/vrfs/1/">vrf1</a>	39	1
30	2017-05-02 16:16:34.355449+00	1	1	Created aggregate <a href="/ipam/aggregates/1/">10.0.0.0/8</a>	41	1
31	2017-05-02 16:16:54.897341+00	2	1	Created prefix <a href="/ipam/prefixes/2/">10.1.0.0/16</a>	44	1
32	2017-05-02 16:17:33.924852+00	3	1	Created prefix <a href="/ipam/prefixes/3/">10.2.0.0/16</a>	44	1
33	2017-05-02 16:18:48.793725+00	2	1	Created role vlan_role1	36	1
34	2017-05-02 16:19:07.102739+00	1	1	Created VLAN group <a href="/ipam/vlans/?group_id=1">test_site2 - vlan1</a>	38	1
35	2017-05-02 16:19:33.294624+00	1	1	Created VLAN <a href="/ipam/vlans/1/">1 (vlan_1)</a>	43	1
36	2017-05-02 16:19:40.640619+00	1	3	Modified VLAN <a href="/ipam/vlans/1/">1 (vlan_1)</a>	43	1
37	2017-05-02 16:19:51.058089+00	3	3	Modified prefix <a href="/ipam/prefixes/3/">10.2.0.0/16</a>	44	1
38	2017-05-02 17:28:56.290564+00	2	1	Created VRF <a href="/ipam/vrfs/2/">vrf2</a>	39	1
39	2017-05-03 08:40:59.223096+00	1	3	Modified IP address <a href="/ipam/ip-addresses/1/">10.0.0.1/8</a>	40	1
40	2017-05-03 08:42:55.726122+00	2	3	Modified interface interface1	15	1
41	2017-05-04 08:45:49.483978+00	2	1	Created IP address <a href="/ipam/ip-addresses/2/">10.1.0.0/24</a>	40	1
42	2017-05-04 08:46:18.894004+00	2	3	Modified device <a href="/dcim/devices/2/">device2</a>	19	1
43	2017-05-04 08:46:42.974427+00	1	1	Created service service22 (22/TCP)	37	1
44	2017-05-04 08:48:24.564801+00	2	3	Modified device <a href="/dcim/devices/2/">device2</a>	19	1
45	2017-05-04 08:49:16.213345+00	2	1	Created device type <a href="/dcim/device-types/2/">parent1</a>	34	1
46	2017-05-04 08:49:31.927165+00	3	1	Created device type <a href="/dcim/device-types/3/">child1</a>	34	1
47	2017-05-04 08:49:53.772606+00	3	1	Created device <a href="/dcim/devices/3/">parent_device1</a>	19	1
48	2017-05-04 08:50:11.299003+00	4	1	Created device <a href="/dcim/devices/4/">child_device1</a>	19	1
49	2017-05-04 08:51:34.512043+00	3	3	Modified device <a href="/dcim/devices/3/">parent_device1</a>	19	1
50	2017-05-04 08:51:56.366498+00	4	3	Modified device <a href="/dcim/devices/4/">child_device1</a>	19	1
82	2017-05-05 05:09:11.53421+00	1	3	Modified device <a href="/dcim/devices/1/">device1</a>	19	1
83	2017-05-05 05:09:11.692162+00	1	3	Modified device <a href="/dcim/devices/1/">device1</a>	19	1
84	2017-05-05 06:11:48.996161+00	4	1	Created prefix <a href="/ipam/prefixes/4/">2001:db8::/32</a>	44	1
85	2017-05-05 06:12:41.608883+00	3	1	Created IP address <a href="/ipam/ip-addresses/3/">2001:db8:aaaa:bbbb::1/64</a>	40	1
86	2017-05-05 06:14:02.272252+00	\N	5	Deleted IP address 2001:db8:aaaa:bbbb::1/64	40	1
87	2017-05-05 06:14:59.990885+00	\N	5	Deleted IP address 2001:db8:aaaa:bbbb::1/64	40	1
\.


--
-- Name: extras_useraction_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('extras_useraction_id_seq', 87, true);


--
-- Data for Name: ipam_aggregate; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY ipam_aggregate (id, created, last_updated, family, prefix, date_added, description, rir_id) FROM stdin;
1	2017-05-02	2017-05-02 16:16:34.340373+00	4	10.0.0.0/8	\N		1
\.


--
-- Name: ipam_aggregate_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('ipam_aggregate_id_seq', 1, true);


--
-- Data for Name: ipam_ipaddress; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY ipam_ipaddress (id, created, last_updated, family, address, description, interface_id, nat_inside_id, vrf_id, tenant_id, status) FROM stdin;
1	2017-04-27	2017-05-03 08:44:07.873129+00	4	10.0.0.1/8	description	3	\N	2	3	1
2	2017-05-04	2017-05-04 08:45:49.461543+00	4	10.1.0.0/24		\N	\N	\N	\N	1
5	2017-05-05	2017-05-05 06:15:12.959253+00	6	2001:db8:aaaa:bbbb::1/64		3	\N	\N	\N	1
\.


--
-- Name: ipam_ipaddress_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('ipam_ipaddress_id_seq', 5, true);


--
-- Data for Name: ipam_prefix; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY ipam_prefix (id, created, last_updated, family, prefix, status, description, role_id, site_id, vlan_id, vrf_id, tenant_id, is_pool) FROM stdin;
1	2017-04-27	2017-04-27 08:35:52.114667+00	4	10.0.0.0/8	1		\N	\N	\N	\N	\N	f
2	2017-05-02	2017-05-02 16:16:54.880489+00	4	10.1.0.0/16	1		\N	\N	\N	\N	\N	t
3	2017-05-02	2017-05-02 16:19:51.04855+00	4	10.2.0.0/16	0	desc1	1	2	1	1	1	f
4	2017-05-05	2017-05-05 06:11:48.97662+00	6	2001:db8::/32	1	Documentation Prefix	\N	\N	\N	\N	\N	f
\.


--
-- Name: ipam_prefix_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('ipam_prefix_id_seq', 4, true);


--
-- Data for Name: ipam_rir; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY ipam_rir (id, name, slug, is_private) FROM stdin;
1	rir1	rir1	t
2	rir2	rir2	f
\.


--
-- Name: ipam_rir_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('ipam_rir_id_seq', 2, true);


--
-- Data for Name: ipam_role; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY ipam_role (id, name, slug, weight) FROM stdin;
1	role1	role1	1000
2	vlan_role1	vlan_role1	1000
\.


--
-- Name: ipam_role_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('ipam_role_id_seq', 2, true);


--
-- Data for Name: ipam_service; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY ipam_service (id, created, last_updated, name, protocol, port, description, device_id) FROM stdin;
1	2017-05-04	2017-05-04 08:46:42.956718+00	service22	6	22		2
\.


--
-- Name: ipam_service_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('ipam_service_id_seq', 1, true);


--
-- Data for Name: ipam_service_ipaddresses; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY ipam_service_ipaddresses (id, service_id, ipaddress_id) FROM stdin;
\.


--
-- Name: ipam_service_ipaddresses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('ipam_service_ipaddresses_id_seq', 1, false);


--
-- Data for Name: ipam_vlan; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY ipam_vlan (id, created, last_updated, vid, name, status, role_id, site_id, group_id, description, tenant_id) FROM stdin;
1	2017-05-02	2017-05-02 16:19:40.629943+00	1	vlan_1	1	2	2	1	desc1	3
\.


--
-- Name: ipam_vlan_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('ipam_vlan_id_seq', 1, true);


--
-- Data for Name: ipam_vlangroup; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY ipam_vlangroup (id, name, slug, site_id) FROM stdin;
1	vlan1	vlan1	2
\.


--
-- Name: ipam_vlangroup_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('ipam_vlangroup_id_seq', 1, true);


--
-- Data for Name: ipam_vrf; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY ipam_vrf (id, created, last_updated, name, rd, description, enforce_unique, tenant_id) FROM stdin;
1	2017-05-02	2017-05-02 16:16:15.100744+00	vrf1	RD1		t	\N
2	2017-05-02	2017-05-02 17:28:56.27037+00	vrf2	RD2		f	3
\.


--
-- Name: ipam_vrf_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('ipam_vrf_id_seq', 2, true);


--
-- Data for Name: secrets_secret; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY secrets_secret (id, created, last_updated, name, ciphertext, hash, device_id, role_id) FROM stdin;
\.


--
-- Name: secrets_secret_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('secrets_secret_id_seq', 1, false);


--
-- Data for Name: secrets_secretrole; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY secrets_secretrole (id, name, slug) FROM stdin;
\.


--
-- Data for Name: secrets_secretrole_groups; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY secrets_secretrole_groups (id, secretrole_id, group_id) FROM stdin;
\.


--
-- Name: secrets_secretrole_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('secrets_secretrole_groups_id_seq', 1, false);


--
-- Name: secrets_secretrole_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('secrets_secretrole_id_seq', 1, false);


--
-- Data for Name: secrets_secretrole_users; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY secrets_secretrole_users (id, secretrole_id, user_id) FROM stdin;
\.


--
-- Name: secrets_secretrole_users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('secrets_secretrole_users_id_seq', 1, false);


--
-- Data for Name: secrets_sessionkey; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY secrets_sessionkey (id, cipher, hash, created, userkey_id) FROM stdin;
\.


--
-- Name: secrets_sessionkey_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('secrets_sessionkey_id_seq', 1, false);


--
-- Data for Name: secrets_userkey; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY secrets_userkey (id, created, last_updated, public_key, master_key_cipher, user_id) FROM stdin;
\.


--
-- Name: secrets_userkey_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('secrets_userkey_id_seq', 1, false);


--
-- Data for Name: tenancy_tenant; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY tenancy_tenant (id, created, last_updated, name, slug, description, comments, group_id) FROM stdin;
1	2017-05-02	2017-05-02 14:46:44.008823+00	tenant1	tenant1			\N
2	2017-05-02	2017-05-02 14:47:28.717035+00	tenant2	tenant2			\N
3	2017-05-02	2017-05-02 14:47:37.281218+00	tenant3	tenant3			1
\.


--
-- Name: tenancy_tenant_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('tenancy_tenant_id_seq', 3, true);


--
-- Data for Name: tenancy_tenantgroup; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY tenancy_tenantgroup (id, name, slug) FROM stdin;
1	Customer	customer
\.


--
-- Name: tenancy_tenantgroup_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('tenancy_tenantgroup_id_seq', 1, true);


--
-- Data for Name: users_token; Type: TABLE DATA; Schema: public; Owner: netbox
--

COPY users_token (id, created, expires, key, write_enabled, description, user_id) FROM stdin;
1	2017-04-12 12:29:32.603744+00	\N	2e35594ec8710e9922d14365a1ea66f27ea69450	t		1
\.


--
-- Name: users_token_id_seq; Type: SEQUENCE SET; Schema: public; Owner: netbox
--

SELECT pg_catalog.setval('users_token_id_seq', 1, true);


--
-- Name: auth_group auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions auth_group_permissions_group_id_permission_id_0cd325b0_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_permission auth_permission_content_type_id_codename_01ab375a_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename);


--
-- Name: auth_permission auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups auth_user_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups auth_user_groups_user_id_group_id_94350c0c_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_group_id_94350c0c_uniq UNIQUE (user_id, group_id);


--
-- Name: auth_user auth_user_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY auth_user
    ADD CONSTRAINT auth_user_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions auth_user_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions auth_user_user_permissions_user_id_permission_id_14a6b632_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_permission_id_14a6b632_uniq UNIQUE (user_id, permission_id);


--
-- Name: auth_user auth_user_username_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY auth_user
    ADD CONSTRAINT auth_user_username_key UNIQUE (username);


--
-- Name: circuits_circuit circuits_circuit_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY circuits_circuit
    ADD CONSTRAINT circuits_circuit_pkey PRIMARY KEY (id);


--
-- Name: circuits_circuit circuits_circuit_provider_id_cid_b6f29862_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY circuits_circuit
    ADD CONSTRAINT circuits_circuit_provider_id_cid_b6f29862_uniq UNIQUE (provider_id, cid);


--
-- Name: circuits_circuittermination circuits_circuittermination_circuit_id_term_side_b13efd0e_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY circuits_circuittermination
    ADD CONSTRAINT circuits_circuittermination_circuit_id_term_side_b13efd0e_uniq UNIQUE (circuit_id, term_side);


--
-- Name: circuits_circuittermination circuits_circuittermination_interface_id_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY circuits_circuittermination
    ADD CONSTRAINT circuits_circuittermination_interface_id_key UNIQUE (interface_id);


--
-- Name: circuits_circuittermination circuits_circuittermination_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY circuits_circuittermination
    ADD CONSTRAINT circuits_circuittermination_pkey PRIMARY KEY (id);


--
-- Name: circuits_circuittype circuits_circuittype_name_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY circuits_circuittype
    ADD CONSTRAINT circuits_circuittype_name_key UNIQUE (name);


--
-- Name: circuits_circuittype circuits_circuittype_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY circuits_circuittype
    ADD CONSTRAINT circuits_circuittype_pkey PRIMARY KEY (id);


--
-- Name: circuits_circuittype circuits_circuittype_slug_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY circuits_circuittype
    ADD CONSTRAINT circuits_circuittype_slug_key UNIQUE (slug);


--
-- Name: circuits_provider circuits_provider_name_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY circuits_provider
    ADD CONSTRAINT circuits_provider_name_key UNIQUE (name);


--
-- Name: circuits_provider circuits_provider_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY circuits_provider
    ADD CONSTRAINT circuits_provider_pkey PRIMARY KEY (id);


--
-- Name: circuits_provider circuits_provider_slug_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY circuits_provider
    ADD CONSTRAINT circuits_provider_slug_key UNIQUE (slug);


--
-- Name: dcim_consoleport dcim_consoleport_cs_port_id_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_consoleport
    ADD CONSTRAINT dcim_consoleport_cs_port_id_key UNIQUE (cs_port_id);


--
-- Name: dcim_consoleport dcim_consoleport_device_id_name_293786b6_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_consoleport
    ADD CONSTRAINT dcim_consoleport_device_id_name_293786b6_uniq UNIQUE (device_id, name);


--
-- Name: dcim_consoleport dcim_consoleport_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_consoleport
    ADD CONSTRAINT dcim_consoleport_pkey PRIMARY KEY (id);


--
-- Name: dcim_consoleporttemplate dcim_consoleporttemplate_device_type_id_name_8208f9ca_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_consoleporttemplate
    ADD CONSTRAINT dcim_consoleporttemplate_device_type_id_name_8208f9ca_uniq UNIQUE (device_type_id, name);


--
-- Name: dcim_consoleporttemplate dcim_consoleporttemplate_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_consoleporttemplate
    ADD CONSTRAINT dcim_consoleporttemplate_pkey PRIMARY KEY (id);


--
-- Name: dcim_consoleserverport dcim_consoleserverport_device_id_name_fb1c5999_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_consoleserverport
    ADD CONSTRAINT dcim_consoleserverport_device_id_name_fb1c5999_uniq UNIQUE (device_id, name);


--
-- Name: dcim_consoleserverport dcim_consoleserverport_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_consoleserverport
    ADD CONSTRAINT dcim_consoleserverport_pkey PRIMARY KEY (id);


--
-- Name: dcim_consoleserverporttemplate dcim_consoleserverportte_device_type_id_name_a05c974d_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_consoleserverporttemplate
    ADD CONSTRAINT dcim_consoleserverportte_device_type_id_name_a05c974d_uniq UNIQUE (device_type_id, name);


--
-- Name: dcim_consoleserverporttemplate dcim_consoleserverporttemplate_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_consoleserverporttemplate
    ADD CONSTRAINT dcim_consoleserverporttemplate_pkey PRIMARY KEY (id);


--
-- Name: dcim_device dcim_device_asset_tag_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_device
    ADD CONSTRAINT dcim_device_asset_tag_key UNIQUE (asset_tag);


--
-- Name: dcim_device dcim_device_name_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_device
    ADD CONSTRAINT dcim_device_name_key UNIQUE (name);


--
-- Name: dcim_device dcim_device_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_device
    ADD CONSTRAINT dcim_device_pkey PRIMARY KEY (id);


--
-- Name: dcim_device dcim_device_primary_ip4_id_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_device
    ADD CONSTRAINT dcim_device_primary_ip4_id_key UNIQUE (primary_ip4_id);


--
-- Name: dcim_device dcim_device_primary_ip6_id_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_device
    ADD CONSTRAINT dcim_device_primary_ip6_id_key UNIQUE (primary_ip6_id);


--
-- Name: dcim_device dcim_device_rack_id_position_face_43208a79_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_device
    ADD CONSTRAINT dcim_device_rack_id_position_face_43208a79_uniq UNIQUE (rack_id, "position", face);


--
-- Name: dcim_devicebay dcim_devicebay_device_id_name_2475a67b_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_devicebay
    ADD CONSTRAINT dcim_devicebay_device_id_name_2475a67b_uniq UNIQUE (device_id, name);


--
-- Name: dcim_devicebay dcim_devicebay_installed_device_id_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_devicebay
    ADD CONSTRAINT dcim_devicebay_installed_device_id_key UNIQUE (installed_device_id);


--
-- Name: dcim_devicebay dcim_devicebay_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_devicebay
    ADD CONSTRAINT dcim_devicebay_pkey PRIMARY KEY (id);


--
-- Name: dcim_devicebaytemplate dcim_devicebaytemplate_device_type_id_name_8f4899fe_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_devicebaytemplate
    ADD CONSTRAINT dcim_devicebaytemplate_device_type_id_name_8f4899fe_uniq UNIQUE (device_type_id, name);


--
-- Name: dcim_devicebaytemplate dcim_devicebaytemplate_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_devicebaytemplate
    ADD CONSTRAINT dcim_devicebaytemplate_pkey PRIMARY KEY (id);


--
-- Name: dcim_devicerole dcim_devicerole_name_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_devicerole
    ADD CONSTRAINT dcim_devicerole_name_key UNIQUE (name);


--
-- Name: dcim_devicerole dcim_devicerole_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_devicerole
    ADD CONSTRAINT dcim_devicerole_pkey PRIMARY KEY (id);


--
-- Name: dcim_devicerole dcim_devicerole_slug_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_devicerole
    ADD CONSTRAINT dcim_devicerole_slug_key UNIQUE (slug);


--
-- Name: dcim_devicetype dcim_devicetype_manufacturer_id_model_17948c0c_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_devicetype
    ADD CONSTRAINT dcim_devicetype_manufacturer_id_model_17948c0c_uniq UNIQUE (manufacturer_id, model);


--
-- Name: dcim_devicetype dcim_devicetype_manufacturer_id_slug_a0b931cb_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_devicetype
    ADD CONSTRAINT dcim_devicetype_manufacturer_id_slug_a0b931cb_uniq UNIQUE (manufacturer_id, slug);


--
-- Name: dcim_devicetype dcim_devicetype_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_devicetype
    ADD CONSTRAINT dcim_devicetype_pkey PRIMARY KEY (id);


--
-- Name: dcim_interface dcim_interface_device_id_name_bffc4ec4_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_interface
    ADD CONSTRAINT dcim_interface_device_id_name_bffc4ec4_uniq UNIQUE (device_id, name);


--
-- Name: dcim_interface dcim_interface_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_interface
    ADD CONSTRAINT dcim_interface_pkey PRIMARY KEY (id);


--
-- Name: dcim_interfaceconnection dcim_interfaceconnection_interface_a_id_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_interfaceconnection
    ADD CONSTRAINT dcim_interfaceconnection_interface_a_id_key UNIQUE (interface_a_id);


--
-- Name: dcim_interfaceconnection dcim_interfaceconnection_interface_b_id_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_interfaceconnection
    ADD CONSTRAINT dcim_interfaceconnection_interface_b_id_key UNIQUE (interface_b_id);


--
-- Name: dcim_interfaceconnection dcim_interfaceconnection_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_interfaceconnection
    ADD CONSTRAINT dcim_interfaceconnection_pkey PRIMARY KEY (id);


--
-- Name: dcim_interfacetemplate dcim_interfacetemplate_device_type_id_name_3a847237_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_interfacetemplate
    ADD CONSTRAINT dcim_interfacetemplate_device_type_id_name_3a847237_uniq UNIQUE (device_type_id, name);


--
-- Name: dcim_interfacetemplate dcim_interfacetemplate_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_interfacetemplate
    ADD CONSTRAINT dcim_interfacetemplate_pkey PRIMARY KEY (id);


--
-- Name: dcim_manufacturer dcim_manufacturer_name_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_manufacturer
    ADD CONSTRAINT dcim_manufacturer_name_key UNIQUE (name);


--
-- Name: dcim_manufacturer dcim_manufacturer_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_manufacturer
    ADD CONSTRAINT dcim_manufacturer_pkey PRIMARY KEY (id);


--
-- Name: dcim_manufacturer dcim_manufacturer_slug_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_manufacturer
    ADD CONSTRAINT dcim_manufacturer_slug_key UNIQUE (slug);


--
-- Name: dcim_inventoryitem dcim_module_device_id_parent_id_name_4d8292af_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_inventoryitem
    ADD CONSTRAINT dcim_module_device_id_parent_id_name_4d8292af_uniq UNIQUE (device_id, parent_id, name);


--
-- Name: dcim_inventoryitem dcim_module_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_inventoryitem
    ADD CONSTRAINT dcim_module_pkey PRIMARY KEY (id);


--
-- Name: dcim_platform dcim_platform_name_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_platform
    ADD CONSTRAINT dcim_platform_name_key UNIQUE (name);


--
-- Name: dcim_platform dcim_platform_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_platform
    ADD CONSTRAINT dcim_platform_pkey PRIMARY KEY (id);


--
-- Name: dcim_platform dcim_platform_slug_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_platform
    ADD CONSTRAINT dcim_platform_slug_key UNIQUE (slug);


--
-- Name: dcim_poweroutlet dcim_poweroutlet_device_id_name_981b00c1_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_poweroutlet
    ADD CONSTRAINT dcim_poweroutlet_device_id_name_981b00c1_uniq UNIQUE (device_id, name);


--
-- Name: dcim_poweroutlet dcim_poweroutlet_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_poweroutlet
    ADD CONSTRAINT dcim_poweroutlet_pkey PRIMARY KEY (id);


--
-- Name: dcim_poweroutlettemplate dcim_poweroutlettemplate_device_type_id_name_eafbb07d_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_poweroutlettemplate
    ADD CONSTRAINT dcim_poweroutlettemplate_device_type_id_name_eafbb07d_uniq UNIQUE (device_type_id, name);


--
-- Name: dcim_poweroutlettemplate dcim_poweroutlettemplate_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_poweroutlettemplate
    ADD CONSTRAINT dcim_poweroutlettemplate_pkey PRIMARY KEY (id);


--
-- Name: dcim_powerport dcim_powerport_device_id_name_948af82c_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_powerport
    ADD CONSTRAINT dcim_powerport_device_id_name_948af82c_uniq UNIQUE (device_id, name);


--
-- Name: dcim_powerport dcim_powerport_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_powerport
    ADD CONSTRAINT dcim_powerport_pkey PRIMARY KEY (id);


--
-- Name: dcim_powerport dcim_powerport_power_outlet_id_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_powerport
    ADD CONSTRAINT dcim_powerport_power_outlet_id_key UNIQUE (power_outlet_id);


--
-- Name: dcim_powerporttemplate dcim_powerporttemplate_device_type_id_name_b4e9689f_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_powerporttemplate
    ADD CONSTRAINT dcim_powerporttemplate_device_type_id_name_b4e9689f_uniq UNIQUE (device_type_id, name);


--
-- Name: dcim_powerporttemplate dcim_powerporttemplate_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_powerporttemplate
    ADD CONSTRAINT dcim_powerporttemplate_pkey PRIMARY KEY (id);


--
-- Name: dcim_rack dcim_rack_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_rack
    ADD CONSTRAINT dcim_rack_pkey PRIMARY KEY (id);


--
-- Name: dcim_rack dcim_rack_site_id_facility_id_2a1d0860_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_rack
    ADD CONSTRAINT dcim_rack_site_id_facility_id_2a1d0860_uniq UNIQUE (site_id, facility_id);


--
-- Name: dcim_rack dcim_rack_site_id_name_5fde0119_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_rack
    ADD CONSTRAINT dcim_rack_site_id_name_5fde0119_uniq UNIQUE (site_id, name);


--
-- Name: dcim_rackgroup dcim_rackgroup_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_rackgroup
    ADD CONSTRAINT dcim_rackgroup_pkey PRIMARY KEY (id);


--
-- Name: dcim_rackgroup dcim_rackgroup_site_id_name_c9bd921f_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_rackgroup
    ADD CONSTRAINT dcim_rackgroup_site_id_name_c9bd921f_uniq UNIQUE (site_id, name);


--
-- Name: dcim_rackgroup dcim_rackgroup_site_id_slug_7fbfd118_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_rackgroup
    ADD CONSTRAINT dcim_rackgroup_site_id_slug_7fbfd118_uniq UNIQUE (site_id, slug);


--
-- Name: dcim_rackreservation dcim_rackreservation_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_rackreservation
    ADD CONSTRAINT dcim_rackreservation_pkey PRIMARY KEY (id);


--
-- Name: dcim_rackrole dcim_rackrole_name_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_rackrole
    ADD CONSTRAINT dcim_rackrole_name_key UNIQUE (name);


--
-- Name: dcim_rackrole dcim_rackrole_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_rackrole
    ADD CONSTRAINT dcim_rackrole_pkey PRIMARY KEY (id);


--
-- Name: dcim_rackrole dcim_rackrole_slug_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_rackrole
    ADD CONSTRAINT dcim_rackrole_slug_key UNIQUE (slug);


--
-- Name: dcim_region dcim_region_name_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_region
    ADD CONSTRAINT dcim_region_name_key UNIQUE (name);


--
-- Name: dcim_region dcim_region_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_region
    ADD CONSTRAINT dcim_region_pkey PRIMARY KEY (id);


--
-- Name: dcim_region dcim_region_slug_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_region
    ADD CONSTRAINT dcim_region_slug_key UNIQUE (slug);


--
-- Name: dcim_site dcim_site_name_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_site
    ADD CONSTRAINT dcim_site_name_key UNIQUE (name);


--
-- Name: dcim_site dcim_site_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_site
    ADD CONSTRAINT dcim_site_pkey PRIMARY KEY (id);


--
-- Name: dcim_site dcim_site_slug_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_site
    ADD CONSTRAINT dcim_site_slug_key UNIQUE (slug);


--
-- Name: django_admin_log django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type django_content_type_app_label_model_76bd3d3b_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model);


--
-- Name: django_content_type django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_migrations django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: django_session django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: extras_customfield extras_customfield_name_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY extras_customfield
    ADD CONSTRAINT extras_customfield_name_key UNIQUE (name);


--
-- Name: extras_customfield_obj_type extras_customfield_obj_t_customfield_id_contentty_77878958_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY extras_customfield_obj_type
    ADD CONSTRAINT extras_customfield_obj_t_customfield_id_contentty_77878958_uniq UNIQUE (customfield_id, contenttype_id);


--
-- Name: extras_customfield_obj_type extras_customfield_obj_type_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY extras_customfield_obj_type
    ADD CONSTRAINT extras_customfield_obj_type_pkey PRIMARY KEY (id);


--
-- Name: extras_customfield extras_customfield_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY extras_customfield
    ADD CONSTRAINT extras_customfield_pkey PRIMARY KEY (id);


--
-- Name: extras_customfieldchoice extras_customfieldchoice_field_id_value_f959a108_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY extras_customfieldchoice
    ADD CONSTRAINT extras_customfieldchoice_field_id_value_f959a108_uniq UNIQUE (field_id, value);


--
-- Name: extras_customfieldchoice extras_customfieldchoice_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY extras_customfieldchoice
    ADD CONSTRAINT extras_customfieldchoice_pkey PRIMARY KEY (id);


--
-- Name: extras_customfieldvalue extras_customfieldvalue_field_id_obj_type_id_obj_876f6d9c_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY extras_customfieldvalue
    ADD CONSTRAINT extras_customfieldvalue_field_id_obj_type_id_obj_876f6d9c_uniq UNIQUE (field_id, obj_type_id, obj_id);


--
-- Name: extras_customfieldvalue extras_customfieldvalue_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY extras_customfieldvalue
    ADD CONSTRAINT extras_customfieldvalue_pkey PRIMARY KEY (id);


--
-- Name: extras_exporttemplate extras_exporttemplate_content_type_id_name_edca9b9b_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY extras_exporttemplate
    ADD CONSTRAINT extras_exporttemplate_content_type_id_name_edca9b9b_uniq UNIQUE (content_type_id, name);


--
-- Name: extras_exporttemplate extras_exporttemplate_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY extras_exporttemplate
    ADD CONSTRAINT extras_exporttemplate_pkey PRIMARY KEY (id);


--
-- Name: extras_graph extras_graph_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY extras_graph
    ADD CONSTRAINT extras_graph_pkey PRIMARY KEY (id);


--
-- Name: extras_imageattachment extras_imageattachment_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY extras_imageattachment
    ADD CONSTRAINT extras_imageattachment_pkey PRIMARY KEY (id);


--
-- Name: extras_topologymap extras_topologymap_name_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY extras_topologymap
    ADD CONSTRAINT extras_topologymap_name_key UNIQUE (name);


--
-- Name: extras_topologymap extras_topologymap_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY extras_topologymap
    ADD CONSTRAINT extras_topologymap_pkey PRIMARY KEY (id);


--
-- Name: extras_topologymap extras_topologymap_slug_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY extras_topologymap
    ADD CONSTRAINT extras_topologymap_slug_key UNIQUE (slug);


--
-- Name: extras_useraction extras_useraction_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY extras_useraction
    ADD CONSTRAINT extras_useraction_pkey PRIMARY KEY (id);


--
-- Name: ipam_aggregate ipam_aggregate_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_aggregate
    ADD CONSTRAINT ipam_aggregate_pkey PRIMARY KEY (id);


--
-- Name: ipam_ipaddress ipam_ipaddress_nat_inside_id_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_ipaddress
    ADD CONSTRAINT ipam_ipaddress_nat_inside_id_key UNIQUE (nat_inside_id);


--
-- Name: ipam_ipaddress ipam_ipaddress_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_ipaddress
    ADD CONSTRAINT ipam_ipaddress_pkey PRIMARY KEY (id);


--
-- Name: ipam_prefix ipam_prefix_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_prefix
    ADD CONSTRAINT ipam_prefix_pkey PRIMARY KEY (id);


--
-- Name: ipam_rir ipam_rir_name_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_rir
    ADD CONSTRAINT ipam_rir_name_key UNIQUE (name);


--
-- Name: ipam_rir ipam_rir_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_rir
    ADD CONSTRAINT ipam_rir_pkey PRIMARY KEY (id);


--
-- Name: ipam_rir ipam_rir_slug_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_rir
    ADD CONSTRAINT ipam_rir_slug_key UNIQUE (slug);


--
-- Name: ipam_role ipam_role_name_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_role
    ADD CONSTRAINT ipam_role_name_key UNIQUE (name);


--
-- Name: ipam_role ipam_role_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_role
    ADD CONSTRAINT ipam_role_pkey PRIMARY KEY (id);


--
-- Name: ipam_role ipam_role_slug_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_role
    ADD CONSTRAINT ipam_role_slug_key UNIQUE (slug);


--
-- Name: ipam_service ipam_service_device_id_protocol_port_c33a12a0_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_service
    ADD CONSTRAINT ipam_service_device_id_protocol_port_c33a12a0_uniq UNIQUE (device_id, protocol, port);


--
-- Name: ipam_service_ipaddresses ipam_service_ipaddresses_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_service_ipaddresses
    ADD CONSTRAINT ipam_service_ipaddresses_pkey PRIMARY KEY (id);


--
-- Name: ipam_service_ipaddresses ipam_service_ipaddresses_service_id_ipaddress_id_d019a805_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_service_ipaddresses
    ADD CONSTRAINT ipam_service_ipaddresses_service_id_ipaddress_id_d019a805_uniq UNIQUE (service_id, ipaddress_id);


--
-- Name: ipam_service ipam_service_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_service
    ADD CONSTRAINT ipam_service_pkey PRIMARY KEY (id);


--
-- Name: ipam_vlan ipam_vlan_group_id_name_e53919df_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_vlan
    ADD CONSTRAINT ipam_vlan_group_id_name_e53919df_uniq UNIQUE (group_id, name);


--
-- Name: ipam_vlan ipam_vlan_group_id_vid_5ca4cc47_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_vlan
    ADD CONSTRAINT ipam_vlan_group_id_vid_5ca4cc47_uniq UNIQUE (group_id, vid);


--
-- Name: ipam_vlan ipam_vlan_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_vlan
    ADD CONSTRAINT ipam_vlan_pkey PRIMARY KEY (id);


--
-- Name: ipam_vlangroup ipam_vlangroup_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_vlangroup
    ADD CONSTRAINT ipam_vlangroup_pkey PRIMARY KEY (id);


--
-- Name: ipam_vlangroup ipam_vlangroup_site_id_name_a38e981b_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_vlangroup
    ADD CONSTRAINT ipam_vlangroup_site_id_name_a38e981b_uniq UNIQUE (site_id, name);


--
-- Name: ipam_vlangroup ipam_vlangroup_site_id_slug_6372a304_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_vlangroup
    ADD CONSTRAINT ipam_vlangroup_site_id_slug_6372a304_uniq UNIQUE (site_id, slug);


--
-- Name: ipam_vrf ipam_vrf_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_vrf
    ADD CONSTRAINT ipam_vrf_pkey PRIMARY KEY (id);


--
-- Name: ipam_vrf ipam_vrf_rd_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_vrf
    ADD CONSTRAINT ipam_vrf_rd_key UNIQUE (rd);


--
-- Name: secrets_secret secrets_secret_device_id_role_id_name_f8acc218_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY secrets_secret
    ADD CONSTRAINT secrets_secret_device_id_role_id_name_f8acc218_uniq UNIQUE (device_id, role_id, name);


--
-- Name: secrets_secret secrets_secret_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY secrets_secret
    ADD CONSTRAINT secrets_secret_pkey PRIMARY KEY (id);


--
-- Name: secrets_secretrole_groups secrets_secretrole_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY secrets_secretrole_groups
    ADD CONSTRAINT secrets_secretrole_groups_pkey PRIMARY KEY (id);


--
-- Name: secrets_secretrole_groups secrets_secretrole_groups_secretrole_id_group_id_1c7f7ee5_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY secrets_secretrole_groups
    ADD CONSTRAINT secrets_secretrole_groups_secretrole_id_group_id_1c7f7ee5_uniq UNIQUE (secretrole_id, group_id);


--
-- Name: secrets_secretrole secrets_secretrole_name_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY secrets_secretrole
    ADD CONSTRAINT secrets_secretrole_name_key UNIQUE (name);


--
-- Name: secrets_secretrole secrets_secretrole_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY secrets_secretrole
    ADD CONSTRAINT secrets_secretrole_pkey PRIMARY KEY (id);


--
-- Name: secrets_secretrole secrets_secretrole_slug_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY secrets_secretrole
    ADD CONSTRAINT secrets_secretrole_slug_key UNIQUE (slug);


--
-- Name: secrets_secretrole_users secrets_secretrole_users_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY secrets_secretrole_users
    ADD CONSTRAINT secrets_secretrole_users_pkey PRIMARY KEY (id);


--
-- Name: secrets_secretrole_users secrets_secretrole_users_secretrole_id_user_id_41832d38_uniq; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY secrets_secretrole_users
    ADD CONSTRAINT secrets_secretrole_users_secretrole_id_user_id_41832d38_uniq UNIQUE (secretrole_id, user_id);


--
-- Name: secrets_sessionkey secrets_sessionkey_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY secrets_sessionkey
    ADD CONSTRAINT secrets_sessionkey_pkey PRIMARY KEY (id);


--
-- Name: secrets_sessionkey secrets_sessionkey_userkey_id_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY secrets_sessionkey
    ADD CONSTRAINT secrets_sessionkey_userkey_id_key UNIQUE (userkey_id);


--
-- Name: secrets_userkey secrets_userkey_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY secrets_userkey
    ADD CONSTRAINT secrets_userkey_pkey PRIMARY KEY (id);


--
-- Name: secrets_userkey secrets_userkey_user_id_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY secrets_userkey
    ADD CONSTRAINT secrets_userkey_user_id_key UNIQUE (user_id);


--
-- Name: tenancy_tenant tenancy_tenant_name_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY tenancy_tenant
    ADD CONSTRAINT tenancy_tenant_name_key UNIQUE (name);


--
-- Name: tenancy_tenant tenancy_tenant_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY tenancy_tenant
    ADD CONSTRAINT tenancy_tenant_pkey PRIMARY KEY (id);


--
-- Name: tenancy_tenant tenancy_tenant_slug_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY tenancy_tenant
    ADD CONSTRAINT tenancy_tenant_slug_key UNIQUE (slug);


--
-- Name: tenancy_tenantgroup tenancy_tenantgroup_name_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY tenancy_tenantgroup
    ADD CONSTRAINT tenancy_tenantgroup_name_key UNIQUE (name);


--
-- Name: tenancy_tenantgroup tenancy_tenantgroup_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY tenancy_tenantgroup
    ADD CONSTRAINT tenancy_tenantgroup_pkey PRIMARY KEY (id);


--
-- Name: tenancy_tenantgroup tenancy_tenantgroup_slug_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY tenancy_tenantgroup
    ADD CONSTRAINT tenancy_tenantgroup_slug_key UNIQUE (slug);


--
-- Name: users_token users_token_key_key; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY users_token
    ADD CONSTRAINT users_token_key_key UNIQUE (key);


--
-- Name: users_token users_token_pkey; Type: CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY users_token
    ADD CONSTRAINT users_token_pkey PRIMARY KEY (id);


--
-- Name: auth_group_name_a6ea08ec_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX auth_group_name_a6ea08ec_like ON auth_group USING btree (name varchar_pattern_ops);


--
-- Name: auth_group_permissions_group_id_b120cbf9; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON auth_group_permissions USING btree (group_id);


--
-- Name: auth_group_permissions_permission_id_84c5c92e; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON auth_group_permissions USING btree (permission_id);


--
-- Name: auth_permission_content_type_id_2f476e4b; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX auth_permission_content_type_id_2f476e4b ON auth_permission USING btree (content_type_id);


--
-- Name: auth_user_groups_group_id_97559544; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX auth_user_groups_group_id_97559544 ON auth_user_groups USING btree (group_id);


--
-- Name: auth_user_groups_user_id_6a12ed8b; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX auth_user_groups_user_id_6a12ed8b ON auth_user_groups USING btree (user_id);


--
-- Name: auth_user_user_permissions_permission_id_1fbb5f2c; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX auth_user_user_permissions_permission_id_1fbb5f2c ON auth_user_user_permissions USING btree (permission_id);


--
-- Name: auth_user_user_permissions_user_id_a95ead1b; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX auth_user_user_permissions_user_id_a95ead1b ON auth_user_user_permissions USING btree (user_id);


--
-- Name: auth_user_username_6821ab7c_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX auth_user_username_6821ab7c_like ON auth_user USING btree (username varchar_pattern_ops);


--
-- Name: circuits_circuit_provider_id_d9195418; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX circuits_circuit_provider_id_d9195418 ON circuits_circuit USING btree (provider_id);


--
-- Name: circuits_circuit_tenant_id_812508a5; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX circuits_circuit_tenant_id_812508a5 ON circuits_circuit USING btree (tenant_id);


--
-- Name: circuits_circuit_type_id_1b9f485a; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX circuits_circuit_type_id_1b9f485a ON circuits_circuit USING btree (type_id);


--
-- Name: circuits_circuittermination_circuit_id_257e87e7; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX circuits_circuittermination_circuit_id_257e87e7 ON circuits_circuittermination USING btree (circuit_id);


--
-- Name: circuits_circuittermination_site_id_e6fe5652; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX circuits_circuittermination_site_id_e6fe5652 ON circuits_circuittermination USING btree (site_id);


--
-- Name: circuits_circuittype_name_8256ea9a_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX circuits_circuittype_name_8256ea9a_like ON circuits_circuittype USING btree (name varchar_pattern_ops);


--
-- Name: circuits_circuittype_slug_9b4b3cf9_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX circuits_circuittype_slug_9b4b3cf9_like ON circuits_circuittype USING btree (slug varchar_pattern_ops);


--
-- Name: circuits_provider_name_8f2514f5_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX circuits_provider_name_8f2514f5_like ON circuits_provider USING btree (name varchar_pattern_ops);


--
-- Name: circuits_provider_slug_c3c0aa10_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX circuits_provider_slug_c3c0aa10_like ON circuits_provider USING btree (slug varchar_pattern_ops);


--
-- Name: dcim_consoleport_device_id_f2d90d3c; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_consoleport_device_id_f2d90d3c ON dcim_consoleport USING btree (device_id);


--
-- Name: dcim_consoleporttemplate_device_type_id_075d4015; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_consoleporttemplate_device_type_id_075d4015 ON dcim_consoleporttemplate USING btree (device_type_id);


--
-- Name: dcim_consoleserverport_device_id_d9866581; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_consoleserverport_device_id_d9866581 ON dcim_consoleserverport USING btree (device_id);


--
-- Name: dcim_consoleserverporttemplate_device_type_id_579bdc86; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_consoleserverporttemplate_device_type_id_579bdc86 ON dcim_consoleserverporttemplate USING btree (device_type_id);


--
-- Name: dcim_device_asset_tag_8dac1079_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_device_asset_tag_8dac1079_like ON dcim_device USING btree (asset_tag varchar_pattern_ops);


--
-- Name: dcim_device_device_role_id_682e8188; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_device_device_role_id_682e8188 ON dcim_device USING btree (device_role_id);


--
-- Name: dcim_device_device_type_id_d61b4086; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_device_device_type_id_d61b4086 ON dcim_device USING btree (device_type_id);


--
-- Name: dcim_device_name_cfa61dd8_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_device_name_cfa61dd8_like ON dcim_device USING btree (name varchar_pattern_ops);


--
-- Name: dcim_device_platform_id_468138f1; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_device_platform_id_468138f1 ON dcim_device USING btree (platform_id);


--
-- Name: dcim_device_rack_id_23bde71f; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_device_rack_id_23bde71f ON dcim_device USING btree (rack_id);


--
-- Name: dcim_device_site_id_ff897cf6; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_device_site_id_ff897cf6 ON dcim_device USING btree (site_id);


--
-- Name: dcim_device_tenant_id_dcea7969; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_device_tenant_id_dcea7969 ON dcim_device USING btree (tenant_id);


--
-- Name: dcim_devicebay_device_id_0c8a1218; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_devicebay_device_id_0c8a1218 ON dcim_devicebay USING btree (device_id);


--
-- Name: dcim_devicebaytemplate_device_type_id_f4b24a29; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_devicebaytemplate_device_type_id_f4b24a29 ON dcim_devicebaytemplate USING btree (device_type_id);


--
-- Name: dcim_devicerole_name_1c813306_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_devicerole_name_1c813306_like ON dcim_devicerole USING btree (name varchar_pattern_ops);


--
-- Name: dcim_devicerole_slug_7952643b_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_devicerole_slug_7952643b_like ON dcim_devicerole USING btree (slug varchar_pattern_ops);


--
-- Name: dcim_devicetype_manufacturer_id_a3e8029e; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_devicetype_manufacturer_id_a3e8029e ON dcim_devicetype USING btree (manufacturer_id);


--
-- Name: dcim_devicetype_slug_448745bd; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_devicetype_slug_448745bd ON dcim_devicetype USING btree (slug);


--
-- Name: dcim_devicetype_slug_448745bd_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_devicetype_slug_448745bd_like ON dcim_devicetype USING btree (slug varchar_pattern_ops);


--
-- Name: dcim_interface_device_id_359c6115; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_interface_device_id_359c6115 ON dcim_interface USING btree (device_id);


--
-- Name: dcim_interface_lag_id_ea1a1d12; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_interface_lag_id_ea1a1d12 ON dcim_interface USING btree (lag_id);


--
-- Name: dcim_interfacetemplate_device_type_id_4bfcbfab; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_interfacetemplate_device_type_id_4bfcbfab ON dcim_interfacetemplate USING btree (device_type_id);


--
-- Name: dcim_manufacturer_name_841fcd92_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_manufacturer_name_841fcd92_like ON dcim_manufacturer USING btree (name varchar_pattern_ops);


--
-- Name: dcim_manufacturer_slug_00430749_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_manufacturer_slug_00430749_like ON dcim_manufacturer USING btree (slug varchar_pattern_ops);


--
-- Name: dcim_module_device_id_53cfd5be; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_module_device_id_53cfd5be ON dcim_inventoryitem USING btree (device_id);


--
-- Name: dcim_module_manufacturer_id_95322cbb; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_module_manufacturer_id_95322cbb ON dcim_inventoryitem USING btree (manufacturer_id);


--
-- Name: dcim_module_parent_id_bb5d0341; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_module_parent_id_bb5d0341 ON dcim_inventoryitem USING btree (parent_id);


--
-- Name: dcim_platform_name_c2f04255_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_platform_name_c2f04255_like ON dcim_platform USING btree (name varchar_pattern_ops);


--
-- Name: dcim_platform_slug_b0908ae4_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_platform_slug_b0908ae4_like ON dcim_platform USING btree (slug varchar_pattern_ops);


--
-- Name: dcim_poweroutlet_device_id_286351d7; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_poweroutlet_device_id_286351d7 ON dcim_poweroutlet USING btree (device_id);


--
-- Name: dcim_poweroutlettemplate_device_type_id_26b2316c; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_poweroutlettemplate_device_type_id_26b2316c ON dcim_poweroutlettemplate USING btree (device_type_id);


--
-- Name: dcim_powerport_device_id_ef7185ae; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_powerport_device_id_ef7185ae ON dcim_powerport USING btree (device_id);


--
-- Name: dcim_powerporttemplate_device_type_id_1ddfbfcc; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_powerporttemplate_device_type_id_1ddfbfcc ON dcim_powerporttemplate USING btree (device_type_id);


--
-- Name: dcim_rack_group_id_44e90ea9; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_rack_group_id_44e90ea9 ON dcim_rack USING btree (group_id);


--
-- Name: dcim_rack_role_id_62d6919e; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_rack_role_id_62d6919e ON dcim_rack USING btree (role_id);


--
-- Name: dcim_rack_site_id_403c7b3a; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_rack_site_id_403c7b3a ON dcim_rack USING btree (site_id);


--
-- Name: dcim_rack_tenant_id_7cdf3725; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_rack_tenant_id_7cdf3725 ON dcim_rack USING btree (tenant_id);


--
-- Name: dcim_rackgroup_site_id_13520e89; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_rackgroup_site_id_13520e89 ON dcim_rackgroup USING btree (site_id);


--
-- Name: dcim_rackgroup_slug_3f4582a7; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_rackgroup_slug_3f4582a7 ON dcim_rackgroup USING btree (slug);


--
-- Name: dcim_rackgroup_slug_3f4582a7_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_rackgroup_slug_3f4582a7_like ON dcim_rackgroup USING btree (slug varchar_pattern_ops);


--
-- Name: dcim_rackreservation_rack_id_1ebbaa9b; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_rackreservation_rack_id_1ebbaa9b ON dcim_rackreservation USING btree (rack_id);


--
-- Name: dcim_rackreservation_user_id_0785a527; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_rackreservation_user_id_0785a527 ON dcim_rackreservation USING btree (user_id);


--
-- Name: dcim_rackrole_name_9077cfcc_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_rackrole_name_9077cfcc_like ON dcim_rackrole USING btree (name varchar_pattern_ops);


--
-- Name: dcim_rackrole_slug_40bbcd3a_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_rackrole_slug_40bbcd3a_like ON dcim_rackrole USING btree (slug varchar_pattern_ops);


--
-- Name: dcim_region_level_2cee781b; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_region_level_2cee781b ON dcim_region USING btree (level);


--
-- Name: dcim_region_lft_923d059c; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_region_lft_923d059c ON dcim_region USING btree (lft);


--
-- Name: dcim_region_name_ba5a7082_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_region_name_ba5a7082_like ON dcim_region USING btree (name varchar_pattern_ops);


--
-- Name: dcim_region_parent_id_2486f5d4; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_region_parent_id_2486f5d4 ON dcim_region USING btree (parent_id);


--
-- Name: dcim_region_rght_20f888e3; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_region_rght_20f888e3 ON dcim_region USING btree (rght);


--
-- Name: dcim_region_slug_ff078a66_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_region_slug_ff078a66_like ON dcim_region USING btree (slug varchar_pattern_ops);


--
-- Name: dcim_region_tree_id_a09ea9a7; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_region_tree_id_a09ea9a7 ON dcim_region USING btree (tree_id);


--
-- Name: dcim_site_name_8fe66c76_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_site_name_8fe66c76_like ON dcim_site USING btree (name varchar_pattern_ops);


--
-- Name: dcim_site_region_id_45210932; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_site_region_id_45210932 ON dcim_site USING btree (region_id);


--
-- Name: dcim_site_slug_4412c762_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_site_slug_4412c762_like ON dcim_site USING btree (slug varchar_pattern_ops);


--
-- Name: dcim_site_tenant_id_15e7df63; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX dcim_site_tenant_id_15e7df63 ON dcim_site USING btree (tenant_id);


--
-- Name: django_admin_log_content_type_id_c4bce8eb; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_user_id_c564eba6; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX django_admin_log_user_id_c564eba6 ON django_admin_log USING btree (user_id);


--
-- Name: django_session_expire_date_a5c62663; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX django_session_expire_date_a5c62663 ON django_session USING btree (expire_date);


--
-- Name: django_session_session_key_c0390e0f_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX django_session_session_key_c0390e0f_like ON django_session USING btree (session_key varchar_pattern_ops);


--
-- Name: extras_customfield_name_2fe72707_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX extras_customfield_name_2fe72707_like ON extras_customfield USING btree (name varchar_pattern_ops);


--
-- Name: extras_customfield_obj_type_contenttype_id_6890b714; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX extras_customfield_obj_type_contenttype_id_6890b714 ON extras_customfield_obj_type USING btree (contenttype_id);


--
-- Name: extras_customfield_obj_type_customfield_id_82480f86; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX extras_customfield_obj_type_customfield_id_82480f86 ON extras_customfield_obj_type USING btree (customfield_id);


--
-- Name: extras_customfieldchoice_field_id_35006739; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX extras_customfieldchoice_field_id_35006739 ON extras_customfieldchoice USING btree (field_id);


--
-- Name: extras_customfieldvalue_field_id_1a461f0d; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX extras_customfieldvalue_field_id_1a461f0d ON extras_customfieldvalue USING btree (field_id);


--
-- Name: extras_customfieldvalue_obj_type_id_b750b07b; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX extras_customfieldvalue_obj_type_id_b750b07b ON extras_customfieldvalue USING btree (obj_type_id);


--
-- Name: extras_exporttemplate_content_type_id_59737e21; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX extras_exporttemplate_content_type_id_59737e21 ON extras_exporttemplate USING btree (content_type_id);


--
-- Name: extras_imageattachment_content_type_id_90e0643d; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX extras_imageattachment_content_type_id_90e0643d ON extras_imageattachment USING btree (content_type_id);


--
-- Name: extras_topologymap_name_f377ebf1_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX extras_topologymap_name_f377ebf1_like ON extras_topologymap USING btree (name varchar_pattern_ops);


--
-- Name: extras_topologymap_site_id_b56b3ceb; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX extras_topologymap_site_id_b56b3ceb ON extras_topologymap USING btree (site_id);


--
-- Name: extras_topologymap_slug_9ba3d31e_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX extras_topologymap_slug_9ba3d31e_like ON extras_topologymap USING btree (slug varchar_pattern_ops);


--
-- Name: extras_useraction_content_type_id_99f782d7; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX extras_useraction_content_type_id_99f782d7 ON extras_useraction USING btree (content_type_id);


--
-- Name: extras_useraction_user_id_8aacec56; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX extras_useraction_user_id_8aacec56 ON extras_useraction USING btree (user_id);


--
-- Name: ipam_aggregate_rir_id_ef7a27bd; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX ipam_aggregate_rir_id_ef7a27bd ON ipam_aggregate USING btree (rir_id);


--
-- Name: ipam_ipaddress_interface_id_91e71d9d; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX ipam_ipaddress_interface_id_91e71d9d ON ipam_ipaddress USING btree (interface_id);


--
-- Name: ipam_ipaddress_tenant_id_ac55acfd; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX ipam_ipaddress_tenant_id_ac55acfd ON ipam_ipaddress USING btree (tenant_id);


--
-- Name: ipam_ipaddress_vrf_id_51fcc59b; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX ipam_ipaddress_vrf_id_51fcc59b ON ipam_ipaddress USING btree (vrf_id);


--
-- Name: ipam_prefix_role_id_0a98d415; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX ipam_prefix_role_id_0a98d415 ON ipam_prefix USING btree (role_id);


--
-- Name: ipam_prefix_site_id_0b20df05; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX ipam_prefix_site_id_0b20df05 ON ipam_prefix USING btree (site_id);


--
-- Name: ipam_prefix_tenant_id_7ba1fcc4; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX ipam_prefix_tenant_id_7ba1fcc4 ON ipam_prefix USING btree (tenant_id);


--
-- Name: ipam_prefix_vlan_id_1db91bff; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX ipam_prefix_vlan_id_1db91bff ON ipam_prefix USING btree (vlan_id);


--
-- Name: ipam_prefix_vrf_id_34f78ed0; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX ipam_prefix_vrf_id_34f78ed0 ON ipam_prefix USING btree (vrf_id);


--
-- Name: ipam_rir_name_64a71982_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX ipam_rir_name_64a71982_like ON ipam_rir USING btree (name varchar_pattern_ops);


--
-- Name: ipam_rir_slug_ff1a369a_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX ipam_rir_slug_ff1a369a_like ON ipam_rir USING btree (slug varchar_pattern_ops);


--
-- Name: ipam_role_name_13784849_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX ipam_role_name_13784849_like ON ipam_role USING btree (name varchar_pattern_ops);


--
-- Name: ipam_role_slug_309ca14c_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX ipam_role_slug_309ca14c_like ON ipam_role USING btree (slug varchar_pattern_ops);


--
-- Name: ipam_service_device_id_b4d2bb9c; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX ipam_service_device_id_b4d2bb9c ON ipam_service USING btree (device_id);


--
-- Name: ipam_service_ipaddresses_ipaddress_id_b4138c6d; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX ipam_service_ipaddresses_ipaddress_id_b4138c6d ON ipam_service_ipaddresses USING btree (ipaddress_id);


--
-- Name: ipam_service_ipaddresses_service_id_ae26b9ab; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX ipam_service_ipaddresses_service_id_ae26b9ab ON ipam_service_ipaddresses USING btree (service_id);


--
-- Name: ipam_vlan_group_id_88cbfa62; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX ipam_vlan_group_id_88cbfa62 ON ipam_vlan USING btree (group_id);


--
-- Name: ipam_vlan_role_id_f5015962; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX ipam_vlan_role_id_f5015962 ON ipam_vlan USING btree (role_id);


--
-- Name: ipam_vlan_site_id_a59334e3; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX ipam_vlan_site_id_a59334e3 ON ipam_vlan USING btree (site_id);


--
-- Name: ipam_vlan_tenant_id_71a8290d; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX ipam_vlan_tenant_id_71a8290d ON ipam_vlan USING btree (tenant_id);


--
-- Name: ipam_vlangroup_site_id_264f36f6; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX ipam_vlangroup_site_id_264f36f6 ON ipam_vlangroup USING btree (site_id);


--
-- Name: ipam_vlangroup_slug_40abcf6b; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX ipam_vlangroup_slug_40abcf6b ON ipam_vlangroup USING btree (slug);


--
-- Name: ipam_vlangroup_slug_40abcf6b_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX ipam_vlangroup_slug_40abcf6b_like ON ipam_vlangroup USING btree (slug varchar_pattern_ops);


--
-- Name: ipam_vrf_rd_0ac1bde1_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX ipam_vrf_rd_0ac1bde1_like ON ipam_vrf USING btree (rd varchar_pattern_ops);


--
-- Name: ipam_vrf_tenant_id_498b0051; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX ipam_vrf_tenant_id_498b0051 ON ipam_vrf USING btree (tenant_id);


--
-- Name: secrets_secret_device_id_c7c13124; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX secrets_secret_device_id_c7c13124 ON secrets_secret USING btree (device_id);


--
-- Name: secrets_secret_role_id_39d9347f; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX secrets_secret_role_id_39d9347f ON secrets_secret USING btree (role_id);


--
-- Name: secrets_secretrole_groups_group_id_a687dd10; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX secrets_secretrole_groups_group_id_a687dd10 ON secrets_secretrole_groups USING btree (group_id);


--
-- Name: secrets_secretrole_groups_secretrole_id_3cf0338b; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX secrets_secretrole_groups_secretrole_id_3cf0338b ON secrets_secretrole_groups USING btree (secretrole_id);


--
-- Name: secrets_secretrole_name_7b6ee7a4_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX secrets_secretrole_name_7b6ee7a4_like ON secrets_secretrole USING btree (name varchar_pattern_ops);


--
-- Name: secrets_secretrole_slug_a06c885e_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX secrets_secretrole_slug_a06c885e_like ON secrets_secretrole USING btree (slug varchar_pattern_ops);


--
-- Name: secrets_secretrole_users_secretrole_id_d2eac298; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX secrets_secretrole_users_secretrole_id_d2eac298 ON secrets_secretrole_users USING btree (secretrole_id);


--
-- Name: secrets_secretrole_users_user_id_25be95ad; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX secrets_secretrole_users_user_id_25be95ad ON secrets_secretrole_users USING btree (user_id);


--
-- Name: tenancy_tenant_group_id_7daef6f4; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX tenancy_tenant_group_id_7daef6f4 ON tenancy_tenant USING btree (group_id);


--
-- Name: tenancy_tenant_name_f6e5b2f5_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX tenancy_tenant_name_f6e5b2f5_like ON tenancy_tenant USING btree (name varchar_pattern_ops);


--
-- Name: tenancy_tenant_slug_0716575e_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX tenancy_tenant_slug_0716575e_like ON tenancy_tenant USING btree (slug varchar_pattern_ops);


--
-- Name: tenancy_tenantgroup_name_53363199_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX tenancy_tenantgroup_name_53363199_like ON tenancy_tenantgroup USING btree (name varchar_pattern_ops);


--
-- Name: tenancy_tenantgroup_slug_e2af1cb6_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX tenancy_tenantgroup_slug_e2af1cb6_like ON tenancy_tenantgroup USING btree (slug varchar_pattern_ops);


--
-- Name: users_token_key_820deccd_like; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX users_token_key_820deccd_like ON users_token USING btree (key varchar_pattern_ops);


--
-- Name: users_token_user_id_af964690; Type: INDEX; Schema: public; Owner: netbox
--

CREATE INDEX users_token_user_id_af964690 ON users_token USING btree (user_id);


--
-- Name: auth_group_permissions auth_group_permissio_permission_id_84c5c92e_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions auth_group_permissions_group_id_b120cbf9_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_permission auth_permission_content_type_id_2f476e4b_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_groups auth_user_groups_group_id_97559544_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_group_id_97559544_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_groups auth_user_groups_user_id_6a12ed8b_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_6a12ed8b_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_user_permissions auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_user_permissions auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: circuits_circuit circuits_circuit_provider_id_d9195418_fk_circuits_provider_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY circuits_circuit
    ADD CONSTRAINT circuits_circuit_provider_id_d9195418_fk_circuits_provider_id FOREIGN KEY (provider_id) REFERENCES circuits_provider(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: circuits_circuit circuits_circuit_tenant_id_812508a5_fk_tenancy_tenant_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY circuits_circuit
    ADD CONSTRAINT circuits_circuit_tenant_id_812508a5_fk_tenancy_tenant_id FOREIGN KEY (tenant_id) REFERENCES tenancy_tenant(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: circuits_circuit circuits_circuit_type_id_1b9f485a_fk_circuits_circuittype_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY circuits_circuit
    ADD CONSTRAINT circuits_circuit_type_id_1b9f485a_fk_circuits_circuittype_id FOREIGN KEY (type_id) REFERENCES circuits_circuittype(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: circuits_circuittermination circuits_circuitterm_circuit_id_257e87e7_fk_circuits_; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY circuits_circuittermination
    ADD CONSTRAINT circuits_circuitterm_circuit_id_257e87e7_fk_circuits_ FOREIGN KEY (circuit_id) REFERENCES circuits_circuit(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: circuits_circuittermination circuits_circuitterm_interface_id_a147755f_fk_dcim_inte; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY circuits_circuittermination
    ADD CONSTRAINT circuits_circuitterm_interface_id_a147755f_fk_dcim_inte FOREIGN KEY (interface_id) REFERENCES dcim_interface(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: circuits_circuittermination circuits_circuittermination_site_id_e6fe5652_fk_dcim_site_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY circuits_circuittermination
    ADD CONSTRAINT circuits_circuittermination_site_id_e6fe5652_fk_dcim_site_id FOREIGN KEY (site_id) REFERENCES dcim_site(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_consoleport dcim_consoleport_cs_port_id_41f056d5_fk_dcim_cons; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_consoleport
    ADD CONSTRAINT dcim_consoleport_cs_port_id_41f056d5_fk_dcim_cons FOREIGN KEY (cs_port_id) REFERENCES dcim_consoleserverport(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_consoleport dcim_consoleport_device_id_f2d90d3c_fk_dcim_device_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_consoleport
    ADD CONSTRAINT dcim_consoleport_device_id_f2d90d3c_fk_dcim_device_id FOREIGN KEY (device_id) REFERENCES dcim_device(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_consoleporttemplate dcim_consoleporttemp_device_type_id_075d4015_fk_dcim_devi; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_consoleporttemplate
    ADD CONSTRAINT dcim_consoleporttemp_device_type_id_075d4015_fk_dcim_devi FOREIGN KEY (device_type_id) REFERENCES dcim_devicetype(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_consoleserverporttemplate dcim_consoleserverpo_device_type_id_579bdc86_fk_dcim_devi; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_consoleserverporttemplate
    ADD CONSTRAINT dcim_consoleserverpo_device_type_id_579bdc86_fk_dcim_devi FOREIGN KEY (device_type_id) REFERENCES dcim_devicetype(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_consoleserverport dcim_consoleserverport_device_id_d9866581_fk_dcim_device_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_consoleserverport
    ADD CONSTRAINT dcim_consoleserverport_device_id_d9866581_fk_dcim_device_id FOREIGN KEY (device_id) REFERENCES dcim_device(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_device dcim_device_device_role_id_682e8188_fk_dcim_devicerole_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_device
    ADD CONSTRAINT dcim_device_device_role_id_682e8188_fk_dcim_devicerole_id FOREIGN KEY (device_role_id) REFERENCES dcim_devicerole(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_device dcim_device_device_type_id_d61b4086_fk_dcim_devicetype_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_device
    ADD CONSTRAINT dcim_device_device_type_id_d61b4086_fk_dcim_devicetype_id FOREIGN KEY (device_type_id) REFERENCES dcim_devicetype(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_device dcim_device_platform_id_468138f1_fk_dcim_platform_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_device
    ADD CONSTRAINT dcim_device_platform_id_468138f1_fk_dcim_platform_id FOREIGN KEY (platform_id) REFERENCES dcim_platform(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_device dcim_device_primary_ip4_id_2ccd943a_fk_ipam_ipaddress_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_device
    ADD CONSTRAINT dcim_device_primary_ip4_id_2ccd943a_fk_ipam_ipaddress_id FOREIGN KEY (primary_ip4_id) REFERENCES ipam_ipaddress(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_device dcim_device_primary_ip6_id_d180fe91_fk_ipam_ipaddress_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_device
    ADD CONSTRAINT dcim_device_primary_ip6_id_d180fe91_fk_ipam_ipaddress_id FOREIGN KEY (primary_ip6_id) REFERENCES ipam_ipaddress(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_device dcim_device_rack_id_23bde71f_fk_dcim_rack_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_device
    ADD CONSTRAINT dcim_device_rack_id_23bde71f_fk_dcim_rack_id FOREIGN KEY (rack_id) REFERENCES dcim_rack(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_device dcim_device_site_id_ff897cf6_fk_dcim_site_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_device
    ADD CONSTRAINT dcim_device_site_id_ff897cf6_fk_dcim_site_id FOREIGN KEY (site_id) REFERENCES dcim_site(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_device dcim_device_tenant_id_dcea7969_fk_tenancy_tenant_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_device
    ADD CONSTRAINT dcim_device_tenant_id_dcea7969_fk_tenancy_tenant_id FOREIGN KEY (tenant_id) REFERENCES tenancy_tenant(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_devicebay dcim_devicebay_device_id_0c8a1218_fk_dcim_device_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_devicebay
    ADD CONSTRAINT dcim_devicebay_device_id_0c8a1218_fk_dcim_device_id FOREIGN KEY (device_id) REFERENCES dcim_device(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_devicebay dcim_devicebay_installed_device_id_04618112_fk_dcim_device_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_devicebay
    ADD CONSTRAINT dcim_devicebay_installed_device_id_04618112_fk_dcim_device_id FOREIGN KEY (installed_device_id) REFERENCES dcim_device(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_devicebaytemplate dcim_devicebaytempla_device_type_id_f4b24a29_fk_dcim_devi; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_devicebaytemplate
    ADD CONSTRAINT dcim_devicebaytempla_device_type_id_f4b24a29_fk_dcim_devi FOREIGN KEY (device_type_id) REFERENCES dcim_devicetype(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_devicetype dcim_devicetype_manufacturer_id_a3e8029e_fk_dcim_manu; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_devicetype
    ADD CONSTRAINT dcim_devicetype_manufacturer_id_a3e8029e_fk_dcim_manu FOREIGN KEY (manufacturer_id) REFERENCES dcim_manufacturer(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_interface dcim_interface_device_id_359c6115_fk_dcim_device_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_interface
    ADD CONSTRAINT dcim_interface_device_id_359c6115_fk_dcim_device_id FOREIGN KEY (device_id) REFERENCES dcim_device(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_interface dcim_interface_lag_id_ea1a1d12_fk_dcim_interface_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_interface
    ADD CONSTRAINT dcim_interface_lag_id_ea1a1d12_fk_dcim_interface_id FOREIGN KEY (lag_id) REFERENCES dcim_interface(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_interfaceconnection dcim_interfaceconnec_interface_a_id_503f46c2_fk_dcim_inte; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_interfaceconnection
    ADD CONSTRAINT dcim_interfaceconnec_interface_a_id_503f46c2_fk_dcim_inte FOREIGN KEY (interface_a_id) REFERENCES dcim_interface(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_interfaceconnection dcim_interfaceconnec_interface_b_id_85faa104_fk_dcim_inte; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_interfaceconnection
    ADD CONSTRAINT dcim_interfaceconnec_interface_b_id_85faa104_fk_dcim_inte FOREIGN KEY (interface_b_id) REFERENCES dcim_interface(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_interfacetemplate dcim_interfacetempla_device_type_id_4bfcbfab_fk_dcim_devi; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_interfacetemplate
    ADD CONSTRAINT dcim_interfacetempla_device_type_id_4bfcbfab_fk_dcim_devi FOREIGN KEY (device_type_id) REFERENCES dcim_devicetype(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_inventoryitem dcim_inventoryitem_device_id_033d83f8_fk_dcim_device_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_inventoryitem
    ADD CONSTRAINT dcim_inventoryitem_device_id_033d83f8_fk_dcim_device_id FOREIGN KEY (device_id) REFERENCES dcim_device(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_inventoryitem dcim_inventoryitem_manufacturer_id_dcd1b78a_fk_dcim_manu; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_inventoryitem
    ADD CONSTRAINT dcim_inventoryitem_manufacturer_id_dcd1b78a_fk_dcim_manu FOREIGN KEY (manufacturer_id) REFERENCES dcim_manufacturer(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_inventoryitem dcim_inventoryitem_parent_id_7ebcd457_fk_dcim_inventoryitem_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_inventoryitem
    ADD CONSTRAINT dcim_inventoryitem_parent_id_7ebcd457_fk_dcim_inventoryitem_id FOREIGN KEY (parent_id) REFERENCES dcim_inventoryitem(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_poweroutlet dcim_poweroutlet_device_id_286351d7_fk_dcim_device_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_poweroutlet
    ADD CONSTRAINT dcim_poweroutlet_device_id_286351d7_fk_dcim_device_id FOREIGN KEY (device_id) REFERENCES dcim_device(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_poweroutlettemplate dcim_poweroutlettemp_device_type_id_26b2316c_fk_dcim_devi; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_poweroutlettemplate
    ADD CONSTRAINT dcim_poweroutlettemp_device_type_id_26b2316c_fk_dcim_devi FOREIGN KEY (device_type_id) REFERENCES dcim_devicetype(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_powerport dcim_powerport_device_id_ef7185ae_fk_dcim_device_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_powerport
    ADD CONSTRAINT dcim_powerport_device_id_ef7185ae_fk_dcim_device_id FOREIGN KEY (device_id) REFERENCES dcim_device(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_powerport dcim_powerport_power_outlet_id_741276ef_fk_dcim_poweroutlet_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_powerport
    ADD CONSTRAINT dcim_powerport_power_outlet_id_741276ef_fk_dcim_poweroutlet_id FOREIGN KEY (power_outlet_id) REFERENCES dcim_poweroutlet(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_powerporttemplate dcim_powerporttempla_device_type_id_1ddfbfcc_fk_dcim_devi; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_powerporttemplate
    ADD CONSTRAINT dcim_powerporttempla_device_type_id_1ddfbfcc_fk_dcim_devi FOREIGN KEY (device_type_id) REFERENCES dcim_devicetype(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_rack dcim_rack_group_id_44e90ea9_fk_dcim_rackgroup_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_rack
    ADD CONSTRAINT dcim_rack_group_id_44e90ea9_fk_dcim_rackgroup_id FOREIGN KEY (group_id) REFERENCES dcim_rackgroup(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_rack dcim_rack_role_id_62d6919e_fk_dcim_rackrole_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_rack
    ADD CONSTRAINT dcim_rack_role_id_62d6919e_fk_dcim_rackrole_id FOREIGN KEY (role_id) REFERENCES dcim_rackrole(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_rack dcim_rack_site_id_403c7b3a_fk_dcim_site_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_rack
    ADD CONSTRAINT dcim_rack_site_id_403c7b3a_fk_dcim_site_id FOREIGN KEY (site_id) REFERENCES dcim_site(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_rack dcim_rack_tenant_id_7cdf3725_fk_tenancy_tenant_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_rack
    ADD CONSTRAINT dcim_rack_tenant_id_7cdf3725_fk_tenancy_tenant_id FOREIGN KEY (tenant_id) REFERENCES tenancy_tenant(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_rackgroup dcim_rackgroup_site_id_13520e89_fk_dcim_site_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_rackgroup
    ADD CONSTRAINT dcim_rackgroup_site_id_13520e89_fk_dcim_site_id FOREIGN KEY (site_id) REFERENCES dcim_site(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_rackreservation dcim_rackreservation_rack_id_1ebbaa9b_fk_dcim_rack_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_rackreservation
    ADD CONSTRAINT dcim_rackreservation_rack_id_1ebbaa9b_fk_dcim_rack_id FOREIGN KEY (rack_id) REFERENCES dcim_rack(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_rackreservation dcim_rackreservation_user_id_0785a527_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_rackreservation
    ADD CONSTRAINT dcim_rackreservation_user_id_0785a527_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_region dcim_region_parent_id_2486f5d4_fk_dcim_region_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_region
    ADD CONSTRAINT dcim_region_parent_id_2486f5d4_fk_dcim_region_id FOREIGN KEY (parent_id) REFERENCES dcim_region(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_site dcim_site_region_id_45210932_fk_dcim_region_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_site
    ADD CONSTRAINT dcim_site_region_id_45210932_fk_dcim_region_id FOREIGN KEY (region_id) REFERENCES dcim_region(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dcim_site dcim_site_tenant_id_15e7df63_fk_tenancy_tenant_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY dcim_site
    ADD CONSTRAINT dcim_site_tenant_id_15e7df63_fk_tenancy_tenant_id FOREIGN KEY (tenant_id) REFERENCES tenancy_tenant(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_content_type_id_c4bce8eb_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_user_id_c564eba6_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: extras_customfield_obj_type extras_customfield_o_contenttype_id_6890b714_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY extras_customfield_obj_type
    ADD CONSTRAINT extras_customfield_o_contenttype_id_6890b714_fk_django_co FOREIGN KEY (contenttype_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: extras_customfield_obj_type extras_customfield_o_customfield_id_82480f86_fk_extras_cu; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY extras_customfield_obj_type
    ADD CONSTRAINT extras_customfield_o_customfield_id_82480f86_fk_extras_cu FOREIGN KEY (customfield_id) REFERENCES extras_customfield(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: extras_customfieldchoice extras_customfieldch_field_id_35006739_fk_extras_cu; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY extras_customfieldchoice
    ADD CONSTRAINT extras_customfieldch_field_id_35006739_fk_extras_cu FOREIGN KEY (field_id) REFERENCES extras_customfield(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: extras_customfieldvalue extras_customfieldva_field_id_1a461f0d_fk_extras_cu; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY extras_customfieldvalue
    ADD CONSTRAINT extras_customfieldva_field_id_1a461f0d_fk_extras_cu FOREIGN KEY (field_id) REFERENCES extras_customfield(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: extras_customfieldvalue extras_customfieldva_obj_type_id_b750b07b_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY extras_customfieldvalue
    ADD CONSTRAINT extras_customfieldva_obj_type_id_b750b07b_fk_django_co FOREIGN KEY (obj_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: extras_exporttemplate extras_exporttemplat_content_type_id_59737e21_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY extras_exporttemplate
    ADD CONSTRAINT extras_exporttemplat_content_type_id_59737e21_fk_django_co FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: extras_imageattachment extras_imageattachme_content_type_id_90e0643d_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY extras_imageattachment
    ADD CONSTRAINT extras_imageattachme_content_type_id_90e0643d_fk_django_co FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: extras_topologymap extras_topologymap_site_id_b56b3ceb_fk_dcim_site_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY extras_topologymap
    ADD CONSTRAINT extras_topologymap_site_id_b56b3ceb_fk_dcim_site_id FOREIGN KEY (site_id) REFERENCES dcim_site(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: extras_useraction extras_useraction_content_type_id_99f782d7_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY extras_useraction
    ADD CONSTRAINT extras_useraction_content_type_id_99f782d7_fk_django_co FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: extras_useraction extras_useraction_user_id_8aacec56_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY extras_useraction
    ADD CONSTRAINT extras_useraction_user_id_8aacec56_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ipam_aggregate ipam_aggregate_rir_id_ef7a27bd_fk_ipam_rir_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_aggregate
    ADD CONSTRAINT ipam_aggregate_rir_id_ef7a27bd_fk_ipam_rir_id FOREIGN KEY (rir_id) REFERENCES ipam_rir(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ipam_ipaddress ipam_ipaddress_interface_id_91e71d9d_fk_dcim_interface_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_ipaddress
    ADD CONSTRAINT ipam_ipaddress_interface_id_91e71d9d_fk_dcim_interface_id FOREIGN KEY (interface_id) REFERENCES dcim_interface(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ipam_ipaddress ipam_ipaddress_nat_inside_id_a45fb7c5_fk_ipam_ipaddress_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_ipaddress
    ADD CONSTRAINT ipam_ipaddress_nat_inside_id_a45fb7c5_fk_ipam_ipaddress_id FOREIGN KEY (nat_inside_id) REFERENCES ipam_ipaddress(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ipam_ipaddress ipam_ipaddress_tenant_id_ac55acfd_fk_tenancy_tenant_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_ipaddress
    ADD CONSTRAINT ipam_ipaddress_tenant_id_ac55acfd_fk_tenancy_tenant_id FOREIGN KEY (tenant_id) REFERENCES tenancy_tenant(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ipam_ipaddress ipam_ipaddress_vrf_id_51fcc59b_fk_ipam_vrf_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_ipaddress
    ADD CONSTRAINT ipam_ipaddress_vrf_id_51fcc59b_fk_ipam_vrf_id FOREIGN KEY (vrf_id) REFERENCES ipam_vrf(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ipam_prefix ipam_prefix_role_id_0a98d415_fk_ipam_role_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_prefix
    ADD CONSTRAINT ipam_prefix_role_id_0a98d415_fk_ipam_role_id FOREIGN KEY (role_id) REFERENCES ipam_role(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ipam_prefix ipam_prefix_site_id_0b20df05_fk_dcim_site_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_prefix
    ADD CONSTRAINT ipam_prefix_site_id_0b20df05_fk_dcim_site_id FOREIGN KEY (site_id) REFERENCES dcim_site(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ipam_prefix ipam_prefix_tenant_id_7ba1fcc4_fk_tenancy_tenant_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_prefix
    ADD CONSTRAINT ipam_prefix_tenant_id_7ba1fcc4_fk_tenancy_tenant_id FOREIGN KEY (tenant_id) REFERENCES tenancy_tenant(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ipam_prefix ipam_prefix_vlan_id_1db91bff_fk_ipam_vlan_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_prefix
    ADD CONSTRAINT ipam_prefix_vlan_id_1db91bff_fk_ipam_vlan_id FOREIGN KEY (vlan_id) REFERENCES ipam_vlan(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ipam_prefix ipam_prefix_vrf_id_34f78ed0_fk_ipam_vrf_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_prefix
    ADD CONSTRAINT ipam_prefix_vrf_id_34f78ed0_fk_ipam_vrf_id FOREIGN KEY (vrf_id) REFERENCES ipam_vrf(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ipam_service ipam_service_device_id_b4d2bb9c_fk_dcim_device_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_service
    ADD CONSTRAINT ipam_service_device_id_b4d2bb9c_fk_dcim_device_id FOREIGN KEY (device_id) REFERENCES dcim_device(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ipam_service_ipaddresses ipam_service_ipaddre_ipaddress_id_b4138c6d_fk_ipam_ipad; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_service_ipaddresses
    ADD CONSTRAINT ipam_service_ipaddre_ipaddress_id_b4138c6d_fk_ipam_ipad FOREIGN KEY (ipaddress_id) REFERENCES ipam_ipaddress(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ipam_service_ipaddresses ipam_service_ipaddresses_service_id_ae26b9ab_fk_ipam_service_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_service_ipaddresses
    ADD CONSTRAINT ipam_service_ipaddresses_service_id_ae26b9ab_fk_ipam_service_id FOREIGN KEY (service_id) REFERENCES ipam_service(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ipam_vlan ipam_vlan_group_id_88cbfa62_fk_ipam_vlangroup_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_vlan
    ADD CONSTRAINT ipam_vlan_group_id_88cbfa62_fk_ipam_vlangroup_id FOREIGN KEY (group_id) REFERENCES ipam_vlangroup(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ipam_vlan ipam_vlan_role_id_f5015962_fk_ipam_role_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_vlan
    ADD CONSTRAINT ipam_vlan_role_id_f5015962_fk_ipam_role_id FOREIGN KEY (role_id) REFERENCES ipam_role(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ipam_vlan ipam_vlan_site_id_a59334e3_fk_dcim_site_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_vlan
    ADD CONSTRAINT ipam_vlan_site_id_a59334e3_fk_dcim_site_id FOREIGN KEY (site_id) REFERENCES dcim_site(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ipam_vlan ipam_vlan_tenant_id_71a8290d_fk_tenancy_tenant_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_vlan
    ADD CONSTRAINT ipam_vlan_tenant_id_71a8290d_fk_tenancy_tenant_id FOREIGN KEY (tenant_id) REFERENCES tenancy_tenant(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ipam_vlangroup ipam_vlangroup_site_id_264f36f6_fk_dcim_site_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_vlangroup
    ADD CONSTRAINT ipam_vlangroup_site_id_264f36f6_fk_dcim_site_id FOREIGN KEY (site_id) REFERENCES dcim_site(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: ipam_vrf ipam_vrf_tenant_id_498b0051_fk_tenancy_tenant_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY ipam_vrf
    ADD CONSTRAINT ipam_vrf_tenant_id_498b0051_fk_tenancy_tenant_id FOREIGN KEY (tenant_id) REFERENCES tenancy_tenant(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: secrets_secret secrets_secret_device_id_c7c13124_fk_dcim_device_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY secrets_secret
    ADD CONSTRAINT secrets_secret_device_id_c7c13124_fk_dcim_device_id FOREIGN KEY (device_id) REFERENCES dcim_device(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: secrets_secret secrets_secret_role_id_39d9347f_fk_secrets_secretrole_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY secrets_secret
    ADD CONSTRAINT secrets_secret_role_id_39d9347f_fk_secrets_secretrole_id FOREIGN KEY (role_id) REFERENCES secrets_secretrole(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: secrets_secretrole_groups secrets_secretrole_g_secretrole_id_3cf0338b_fk_secrets_s; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY secrets_secretrole_groups
    ADD CONSTRAINT secrets_secretrole_g_secretrole_id_3cf0338b_fk_secrets_s FOREIGN KEY (secretrole_id) REFERENCES secrets_secretrole(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: secrets_secretrole_groups secrets_secretrole_groups_group_id_a687dd10_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY secrets_secretrole_groups
    ADD CONSTRAINT secrets_secretrole_groups_group_id_a687dd10_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: secrets_secretrole_users secrets_secretrole_u_secretrole_id_d2eac298_fk_secrets_s; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY secrets_secretrole_users
    ADD CONSTRAINT secrets_secretrole_u_secretrole_id_d2eac298_fk_secrets_s FOREIGN KEY (secretrole_id) REFERENCES secrets_secretrole(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: secrets_secretrole_users secrets_secretrole_users_user_id_25be95ad_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY secrets_secretrole_users
    ADD CONSTRAINT secrets_secretrole_users_user_id_25be95ad_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: secrets_sessionkey secrets_sessionkey_userkey_id_3ca6176b_fk_secrets_userkey_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY secrets_sessionkey
    ADD CONSTRAINT secrets_sessionkey_userkey_id_3ca6176b_fk_secrets_userkey_id FOREIGN KEY (userkey_id) REFERENCES secrets_userkey(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: secrets_userkey secrets_userkey_user_id_13ada46b_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY secrets_userkey
    ADD CONSTRAINT secrets_userkey_user_id_13ada46b_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: tenancy_tenant tenancy_tenant_group_id_7daef6f4_fk_tenancy_tenantgroup_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY tenancy_tenant
    ADD CONSTRAINT tenancy_tenant_group_id_7daef6f4_fk_tenancy_tenantgroup_id FOREIGN KEY (group_id) REFERENCES tenancy_tenantgroup(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: users_token users_token_user_id_af964690_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: netbox
--

ALTER TABLE ONLY users_token
    ADD CONSTRAINT users_token_user_id_af964690_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- PostgreSQL database dump complete
--

