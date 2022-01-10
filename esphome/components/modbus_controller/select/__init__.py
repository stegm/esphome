from esphome.components import select
import esphome.config_validation as cv
import esphome.codegen as cg


from esphome.const import CONF_ADDRESS, CONF_ID
from esphome.jsonschema import jschema_composite
from .. import (
    modbus_controller_ns,
    ModbusController,
    SensorItem,
)
from ..const import (
    CONF_FORCE_NEW_RANGE,
    CONF_MODBUS_CONTROLLER_ID,
    CONF_REGISTER_COUNT,
    CONF_SKIP_UPDATES,
)

DEPENDENCIES = ["modbus_controller"]
CODEOWNERS = ["@stegm"]
CONF_OPTIONSMAP = "optionsmap"

ModbusSelect = modbus_controller_ns.class_(
    "ModbusSelect", cg.Component, select.Select, SensorItem
)


@jschema_composite
def ensure_option_map():
    def validator(value):
        cv.check_not_templatable(value)
        option = cv.All(cv.string_strict)
        mapping = cv.All(cv.int_range(0, 2 ** 64))
        options_map_schema = cv.Schema({option: mapping})
        return options_map_schema(value)

    return validator


CONFIG_SCHEMA = cv.All(
    select.SELECT_SCHEMA.extend(cv.COMPONENT_SCHEMA).extend(
        {
            cv.GenerateID(): cv.declare_id(ModbusSelect),
            cv.GenerateID(CONF_MODBUS_CONTROLLER_ID): cv.use_id(ModbusController),
            cv.Required(CONF_ADDRESS): cv.positive_int,
            cv.Optional(CONF_REGISTER_COUNT, default=1): cv.int_range(1, 8),
            cv.Optional(CONF_SKIP_UPDATES, default=0): cv.positive_int,
            cv.Optional(CONF_FORCE_NEW_RANGE, default=False): cv.boolean,
            cv.Required(CONF_OPTIONSMAP): ensure_option_map(),
        }
    ),
)


async def to_code(config):
    options_map = config[CONF_OPTIONSMAP]
    var = cg.new_Pvariable(
        config[CONF_ID],
        config[CONF_ADDRESS],
        config[CONF_REGISTER_COUNT],
        config[CONF_SKIP_UPDATES],
        config[CONF_FORCE_NEW_RANGE],
        list(options_map.values()),
    )

    await cg.register_component(var, config)
    await select.register_select(var, config, options=list(options_map.keys()))

    parent = await cg.get_variable(config[CONF_MODBUS_CONTROLLER_ID])
    cg.add(parent.add_sensor_item(var))
    cg.add(var.set_parent(parent))
