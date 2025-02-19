import strawberry

from dcim.choices import *

__all__ = (
    'CableEndEnum',
    'CableLengthUnitEnum',
    'CableTypeEnum',
    'ConsolePortSpeedEnum',
    'ConsolePortTypeEnum',
    'DeviceAirflowEnum',
    'DeviceFaceEnum',
    'DeviceStatusEnum',
    'InterfaceDuplexEnum',
    'InterfaceModeEnum',
    'InterfacePoEModeEnum',
    'InterfacePoETypeEnum',
    'InterfaceSpeedEnum',
    'InterfaceTypeEnum',
    'InventoryItemStatusEnum',
    'LinkStatusEnum',
    'LocationStatusEnum',
    'ModuleAirflowEnum',
    'ModuleStatusEnum',
    'PortTypeEnum',
    'PowerFeedPhaseEnum',
    'PowerFeedStatusEnum',
    'PowerFeedSupplyEnum',
    'PowerFeedTypeEnum',
    'PowerOutletFeedLegEnum',
    'PowerOutletTypeEnum',
    'PowerPortTypeEnum',
    'RackAirflowEnum',
    'RackDimensionUnitEnum',
    'RackFormFactorEnum',
    'RackStatusEnum',
    'RackWidthEnum',
    'SiteStatusEnum',
    'SubdeviceRoleEnum',
    'VirtualDeviceContextStatusEnum',
)

CableEndEnum = strawberry.enum(CableEndChoices.as_enum())
CableLengthUnitEnum = strawberry.enum(CableLengthUnitChoices.as_enum())
CableTypeEnum = strawberry.enum(CableTypeChoices.as_enum())
ConsolePortSpeedEnum = strawberry.enum(ConsolePortSpeedChoices.as_enum())
ConsolePortTypeEnum = strawberry.enum(ConsolePortTypeChoices.as_enum())
DeviceAirflowEnum = strawberry.enum(DeviceAirflowChoices.as_enum())
DeviceFaceEnum = strawberry.enum(DeviceFaceChoices.as_enum())
DeviceStatusEnum = strawberry.enum(DeviceStatusChoices.as_enum())
InterfaceDuplexEnum = strawberry.enum(InterfaceDuplexChoices.as_enum())
InterfaceModeEnum = strawberry.enum(InterfaceModeChoices.as_enum())
InterfacePoEModeEnum = strawberry.enum(InterfacePoEModeChoices.as_enum())
InterfacePoETypeEnum = strawberry.enum(InterfacePoETypeChoices.as_enum())
InterfaceSpeedEnum = strawberry.enum(InterfaceSpeedChoices.as_enum())
InterfaceTypeEnum = strawberry.enum(InterfaceTypeChoices.as_enum())
InventoryItemStatusEnum = strawberry.enum(InventoryItemStatusChoices.as_enum())
LinkStatusEnum = strawberry.enum(LinkStatusChoices.as_enum())
LocationStatusEnum = strawberry.enum(LocationStatusChoices.as_enum())
ModuleAirflowEnum = strawberry.enum(ModuleAirflowChoices.as_enum())
ModuleStatusEnum = strawberry.enum(ModuleStatusChoices.as_enum())
PortTypeEnum = strawberry.enum(PortTypeChoices.as_enum())
PowerFeedPhaseEnum = strawberry.enum(PowerFeedPhaseChoices.as_enum())
PowerFeedStatusEnum = strawberry.enum(PowerFeedStatusChoices.as_enum())
PowerFeedSupplyEnum = strawberry.enum(PowerFeedSupplyChoices.as_enum())
PowerFeedTypeEnum = strawberry.enum(PowerFeedTypeChoices.as_enum())
PowerOutletFeedLegEnum = strawberry.enum(PowerOutletFeedLegChoices.as_enum())
PowerOutletTypeEnum = strawberry.enum(PowerOutletTypeChoices.as_enum())
PowerPortTypeEnum = strawberry.enum(PowerPortTypeChoices.as_enum())
RackAirflowEnum = strawberry.enum(RackAirflowChoices.as_enum())
RackDimensionUnitEnum = strawberry.enum(RackDimensionUnitChoices.as_enum())
RackFormFactorEnum = strawberry.enum(RackFormFactorChoices.as_enum())
RackStatusEnum = strawberry.enum(RackStatusChoices.as_enum())
RackWidthEnum = strawberry.enum(RackWidthChoices.as_enum())
SiteStatusEnum = strawberry.enum(SiteStatusChoices.as_enum())
SubdeviceRoleEnum = strawberry.enum(SubdeviceRoleChoices.as_enum())
VirtualDeviceContextStatusEnum = strawberry.enum(VirtualDeviceContextStatusChoices.as_enum())
