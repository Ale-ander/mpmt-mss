from mpmt_mss.rpc import rpc_service, rpc_method

@rpc_service()
class Monitoring:
    """Aggregates one full tooldaq monitoring cycle behind a single RPC call.

    m-pmt-daq-interface's BuildMssMonitoringSnapshot used to make one RPC
    round trip per field (9 total: sensors.read, febmgr.getStatus/getRateAll,
    fpga.getDeadtime/getHousekeeping/getFifoStatus/getFirmwareInfo/
    getClockStatus/getTr32Status) every monitoring_period_sec. snapshot()
    does the same reads as plain (non-RPC) Python calls on this same process
    and returns them all at once, so the client only pays for one network
    round trip. The individual methods on febmgr/fpga/sensors are untouched
    and still directly callable (e.g. by single-value slow control reads).

    Shape matches BuildMssMonitoringSnapshot's own JSON exactly, so that
    side just becomes `snapshot = mss.monitoring.snapshot()` instead of
    assembling the same object field by field.
    """

    def __init__(self, febmgr, fpga, sensors):
        self.febmgr = febmgr
        self.fpga = fpga
        self.sensors = sensors

    @rpc_method
    def snapshot(self):
        return {
            "sensors": self.sensors.read(),
            "channels": self.febmgr.getStatus(),
            "fpga": {
                "deadtime": self.fpga.getDeadtime(),
                "housekeeping": self.fpga.getHousekeeping(),
                "fifo_status": self.fpga.getFifoStatus(),
                "firmware_info": self.fpga.getFirmwareInfo(),
                "rate_all": self.febmgr.getRateAll(),
                "clock": self.fpga.getClockStatus(),
                "tr32": self.fpga.getTr32Status(),
            },
        }
