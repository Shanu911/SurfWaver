from .modwavefieldtransforms import WavefieldTransformRegistry
from .modarray1D import Array1D
import logging
from swprocess.snr import SignaltoNoiseRatio
from .modsensor1C import modSensor1C
from swprocess import Source
import numpy as np

logger = logging.getLogger("swprocess.maswworkflows")


class CMPCCMaswWorkflow():
    """Abstract base class (ABC) defining an MASW workflow."""

    def __init__(self, cmpcc_strm=None, sloc = None, rloc=None, dt=None, settings=None, map_x=None, map_y=None):
        """Perform initialization common to all MaswWorkflows.

        """
        # Set objects state
        self.cmpcc_strm = cmpcc_strm
        self.sloc = sloc
        self.rloc = rloc
        self.settings = settings
        self.map_x = map_x
        self.map_y = map_y
        self.dt = dt
        # Pre-define state variables for ease of reading.
        self.array = None

        # Pre-define optional state variables too.
        self.signal_start = None
        self.signal_end = None
        self.noise = None
        self.signal = None
        self.snr = None

    #def check(self):
    #    """Check array is acceptable for WavefieldTransform."""
    #    if self.array._source_inside:
    #        raise ValueError("Source must be located outside of the array.")

    def trim_offsets(self):
        """Remove receivers outside of the offset range."""
        offsets = self.settings["pre-processing"]["offsets"]
        self.array.trim_offsets(offsets["min"], offsets["max"])

    def detrend(self):
        """Perform linear detrend operation."""
        for sensor in self.array.sensors:
            sensor.detrend()

    def select_noise(self):
        """Select a portion of the record as noise."""
        snr = self.settings["signal-to-noise"]
        if snr["perform"] and self.noise is None:
            # Copy array and trim noise.
            self.noise = Array1D.from_array1d(self.array)
            self.noise.trim(snr["noise"]["begin"], snr["noise"]["end"])

    def trim_time(self):
        """Trim record in the time domain."""
        trim = self.settings["pre-processing"]["trim"]
        if trim["apply"]:
            self.array.trim(trim["begin"], trim["end"])

    def mute(self):
        """Mute record in the time domain."""
        mute = self.settings["pre-processing"]["mute"]
        if mute["apply"]:
            if self.signal_start is None and self.signal_end is None:
                if mute["method"] == "interactive":
                    self.signal_start, self.signal_end = self.array.interactive_mute()
                # TODO (jpv): Implement predefined times for muting.
                else:
                    msg = f"mute type {mute['method']} is unknown, use 'interactive'."
                    raise KeyError(msg)
            else:
                self.array.mute(signal_start=self.signal_start,
                                signal_end=self.signal_end,
                                window_kwargs=mute.get("window kwargs"),
                                )

    def select_signal(self):
        """Select a portion of the record as signal."""
        snr = self.settings["signal-to-noise"]
        if snr["perform"] and self.signal is None:
            # Copy array and trim noise.
            self.signal = Array1D.from_array1d(self.array)
            self.signal.trim(snr["signal"]["begin"], snr["signal"]["end"])

    def calculate_snr(self):
        snr = self.settings["signal-to-noise"]
        process = self.settings["processing"]
        if snr["perform"]:
            self.snr = SignaltoNoiseRatio.from_array1ds(
                self.signal, self.noise,
                fmin=process["fmin"], fmax=process["fmax"],
                pad_snr=snr["pad"]["apply"], df_snr=snr["pad"]["df"])

    def pad(self):
        """Pad record in the time domain."""
        pad = self.settings["pre-processing"]["pad"]
        if pad["apply"]:
            self.array.zero_pad(pad["df"])

    
    def run(self):
        
        
        
        
        sensors = []
        i = 0
        for cmpcc_tr in self.cmpcc_strm:
            cmpcc_tr = np.array(cmpcc_tr)
            cmpcc_tr_t = np.transpose(cmpcc_tr)
            sensor = modSensor1C.from_trace(cmpcc_tr=cmpcc_tr_t, delta=self.dt, x=self.rloc[i])
            sensors.append(sensor)
            i+=1

        # Define source


        source = Source(x=self.sloc, y=0, z=0)
        self.array = Array1D(sensors, source)
        #self.check()
        self.trim_offsets()
        #self.detrend()
        self.select_noise()
        self.trim_time()
        self.mute()
        self.select_signal()
        self.calculate_snr()
        self.pad()
        proc = self.settings["processing"]
        Transform = WavefieldTransformRegistry.create_class(proc["transform"])
        transform = Transform.from_array(array=self.array, settings=proc)
        transform.array = self.array
        if self.settings["signal-to-noise"]["perform"]:
            transform.snr = self.snr.snr
            transform.snr_frequencies = self.snr.frequencies
        return transform

