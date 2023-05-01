class TAMV:
    
    def __init__(self, config):
        self.config = config
        self.printer = self.config.get_printer()
        self.gcode = self.printer.lookup_object('gcode')
        self.offset = self.load_offset()
        self.gcode.register_command('TAMV_SET_OFFSET', self.cmd_TAMV_SET_OFFSET, desc=("TAMV_SET_OFFSET"))
        self.gcode.register_command('TAMV_SAVE_OFFSET', self.cmd_TAMV_SAVE_OFFSET, desc=("TAMV_SAVE_OFFSET"))
        self.printer.register_event_handler("klippy:connect", self.handle_connect)

    def handle_connect(self):
        self.toolhead = self.printer.lookup_object('toolhead')

    def cmd_TAMV_SET_OFFSET(self, gcmd):
        tool = gcmd.get_int('TOOL', -1)
        self.respond("TAMV_SET_OFFSET " + str(gcmd))
        if tool == 1:
            x_adjust = gcmd.get_float('X', None)
            y_adjust = gcmd.get_float('Y', None)
            #z_adjust = gcmd.get_float('Z', None)
            self.offset = [x_adjust, y_adjust, self.offset[2]]

    def cmd_TAMV_SAVE_OFFSET(self, gcmd):
        self.save_offset(self.offset)
        self.respond("Offset saved")

    def get_status(self, eventtime=None):
        status = {
            "current_tool": self.get_current_tool(),
            "offset": self.offset
        }
        return status

    def save_offset(self, offset):
        self.save_variable("xoffset", offset[0])
        self.save_variable("yoffset", offset[1])
        #self.save_variable("zoffset", offset[2])

    def load_offset(self):
        xoffset = self.load_variable("xoffset")
        yoffset = self.load_variable("yoffset")
        zoffset = self.load_variable("zoffset")
        return [xoffset, yoffset, zoffset]

    def get_current_tool(self):
        if not self.is_homed():
            return -1
        if self.toolhead.extruder.get_name() == 'extruder':
            return 0
        if self.toolhead.extruder.get_name() == 'extruder1':
            return 1
        return -1

    def is_homed(self):
        curtime = self.printer.get_reactor().monotonic()
        homed = self.toolhead.get_status(curtime)['homed_axes'].lower()
        if all(axis in homed for axis in ['x','y','z']):
            return True
        return False

    # current_tool = self.load_variable("current_tool")
    def load_variable(self, name):
        save_variables = self.printer.lookup_object('save_variables')
        return save_variables.allVariables[name]

    # self.save_variable("current_tool", tool)
    def save_variable(self, name, value):
        save_variables = self.printer.lookup_object('save_variables')
        save_variables.cmd_SAVE_VARIABLE(self.gcode.create_gcode_command(
            "SAVE_VARIABLE", "SAVE_VARIABLE", {"VARIABLE": name, 'VALUE': value}))

    def respond(self, message):
        self.gcode.respond_raw(message)

def load_config(config):
    return TAMV(config)
