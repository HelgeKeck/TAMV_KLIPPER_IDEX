class TAMV:
    
    def __init__(self, config):
        self.config = config
        self.printer = self.config.get_printer()
        self.gcode = self.printer.lookup_object('gcode')

        self.tool_current = "-2"          # -2 Unknown tool locked, -1 No tool locked, 0 and up are tools.

        self.gcode.register_command('TAMV_SET_TOOL', self.cmd_TAMV_SET_TOOL, desc=("TAMV_SET_TOOL"))
        self.gcode.register_command('TAMV_SET_TOOL_OFFSET', self.cmd_SET_TOOL_OFFSET, desc=("SET_TOOL_OFFSET"))
        self.printer.register_event_handler("klippy:connect", self.handle_connect)

    def handle_connect(self):
        self.toolhead = self.printer.lookup_object('toolhead')

    def cmd_TAMV_SET_TOOL(self, param):
        tool = param.get_int('TOOL', -1) 
        self.tool_current = str(tool)
        save_variables = self.printer.lookup_object('save_variables')
        save_variables.cmd_SAVE_VARIABLE(self.gcode.create_gcode_command(
            "SAVE_VARIABLE", "SAVE_VARIABLE", {"VARIABLE": "tool_current", 'VALUE': tool}))

    def cmd_SET_TOOL_OFFSET(self, gcmd):
        tool_id = gcmd.get_int('TOOL', self.tool_current, minval=0)
        x_pos = gcmd.get_float('X', None)
        x_adjust = gcmd.get_float('X_ADJUST', None)
        y_pos = gcmd.get_float('Y', None)
        y_adjust = gcmd.get_float('Y_ADJUST', None)
        z_pos = gcmd.get_float('Z', None)
        z_adjust = gcmd.get_float('Z_ADJUST', None)

        if tool_id < 0:
            self.gcode.respond_info("cmd_SET_TOOL_TEMPERATURE: Tool " + str(tool_id) + " is not valid.")
            return None

        tool = self.printer.lookup_object("tool " + str(tool_id))
        set_offset_cmd = {}

        if x_pos is not None:
            set_offset_cmd["x_pos"] = x_pos
        elif x_adjust is not None:
            set_offset_cmd["x_adjust"] = x_adjust
        if y_pos is not None:
            set_offset_cmd["y_pos"] = y_pos
        elif y_adjust is not None:
            set_offset_cmd["y_adjust"] = y_adjust
        if z_pos is not None:
            set_offset_cmd["z_pos"] = z_pos
        elif z_adjust is not None:
            set_offset_cmd["z_adjust"] = z_adjust
        if len(set_offset_cmd) > 0:
            tool.set_offset(**set_offset_cmd)

    def get_status(self, eventtime=None):
        status = {
            "tool_current": self.tool_current
        }
        return status

def load_config(config):
    return TAMV(config)
