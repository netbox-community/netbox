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
    'InterfaceKindEnum',
    'InterfaceModeEnum',
    'InterfacePoEModeEnum',
    'InterfacePoETypeEnum',
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

CableEndEnum = strawberry.enum(CableEndChoices.as_enum(prefix='side'))
CableLengthUnitEnum = strawberry.enum(CableLengthUnitChoices.as_enum(prefix='unit'))
CableTypeEnum = strawberry.enum(CableTypeChoices.as_enum(prefix='type'))
ConsolePortSpeedEnum = strawberry.enum(ConsolePortSpeedChoices.as_enum(prefix='speed'))
ConsolePortTypeEnum = strawberry.enum(ConsolePortTypeChoices.as_enum(prefix='type'))
DeviceAirflowEnum = strawberry.enum(DeviceAirflowChoices.as_enum(prefix='airflow'))
DeviceFaceEnum = strawberry.enum(DeviceFaceChoices.as_enum(prefix='face'))
DeviceStatusEnum = strawberry.enum(DeviceStatusChoices.as_enum(prefix='status'))
InterfaceDuplexEnum = strawberry.enum(InterfaceDuplexChoices.as_enum(prefix='duplex'))
InterfaceKindEnum = strawberry.enum(InterfaceKindChoices.as_enum(prefix='kind'))
InterfaceModeEnum = strawberry.enum(InterfaceModeChoices.as_enum(prefix='mode'))
InterfacePoEModeEnum = strawberry.enum(InterfacePoEModeChoices.as_enum(prefix='mode'))
InterfacePoETypeEnum = strawberry.enum(InterfacePoETypeChoices.as_enum())
InterfaceTypeEnum = strawberry.enum(InterfaceTypeChoices.as_enum(prefix='type'))
InventoryItemStatusEnum = strawberry.enum(InventoryItemStatusChoices.as_enum(prefix='status'))
LinkStatusEnum = strawberry.enum(LinkStatusChoices.as_enum(prefix='status'))
LocationStatusEnum = strawberry.enum(LocationStatusChoices.as_enum(prefix='status'))
ModuleAirflowEnum = strawberry.enum(ModuleAirflowChoices.as_enum())
ModuleStatusEnum = strawberry.enum(ModuleStatusChoices.as_enum(prefix='status'))
PortTypeEnum = strawberry.enum(PortTypeChoices.as_enum(prefix='type'))
PowerFeedPhaseEnum = strawberry.enum(PowerFeedPhaseChoices.as_enum(prefix='phase'))
PowerFeedStatusEnum = strawberry.enum(PowerFeedStatusChoices.as_enum(prefix='status'))
PowerFeedSupplyEnum = strawberry.enum(PowerFeedSupplyChoices.as_enum(prefix='supply'))
PowerFeedTypeEnum = strawberry.enum(PowerFeedTypeChoices.as_enum(prefix='type'))
PowerOutletFeedLegEnum = strawberry.enum(PowerOutletFeedLegChoices.as_enum(prefix='feed_leg'))
PowerOutletTypeEnum = strawberry.enum(PowerOutletTypeChoices.as_enum(prefix='type'))
PowerPortTypeEnum = strawberry.enum(PowerPortTypeChoices.as_enum(prefix='type'))
RackAirflowEnum = strawberry.enum(RackAirflowChoices.as_enum())
RackDimensionUnitEnum = strawberry.enum(RackDimensionUnitChoices.as_enum(prefix='unit'))
RackFormFactorEnum = strawberry.enum(RackFormFactorChoices.as_enum(prefix='type'))
RackStatusEnum = strawberry.enum(RackStatusChoices.as_enum(prefix='status'))
RackWidthEnum = strawberry.enum(RackWidthChoices.as_enum(prefix='width'))
SiteStatusEnum = strawberry.enum(SiteStatusChoices.as_enum(prefix='status'))
SubdeviceRoleEnum = strawberry.enum(SubdeviceRoleChoices.as_enum(prefix='role'))
VirtualDeviceContextStatusEnum = strawberry.enum(VirtualDeviceContextStatusChoices.as_enum(prefix='status'))
