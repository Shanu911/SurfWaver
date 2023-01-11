import logging

import numpy as np

from swprocess.maswworkflows import MaswWorkflowRegistry

from .cmpccworkflows import CMPCCMaswWorkflow

logger = logging.getLogger("swprocess.masw")


class modMasw():
    """Customizable Multichannel Analysis of Surface Waves workflow.

    Convenient customer-facing interface for implementing different
    and extensible MASW processing workflows.

    """

    @staticmethod
    def run(cmpcc_strm, sloc, rloc, dt, settings, map_x=lambda x: x, map_y=lambda y: y):
        """Run an MASW workflow from SU or SEGY files.

        Create an instance of an `Masw` object for a specific
        `Masw` workflow. Note that each file should contain
        multiple traces where each trace corresponds to a
        single receiver. The header information for these files must
        be correct and readable. Currently supported file types are
        SEGY and SU.

        Parameters
        ----------
        fnames : str or iterable of str
            File name or iterable of file names.
        settings_fname : str
            JSON settings file detailing how MASW should be performed.
            See `meth: Masw.create_settings_file()` for more
            information.
        map_x, map_y : function, optional
            Functions to convert the x and y coordinates of source and
            receiver information, default is no transformation. Useful
            for converting between coordinate systems.

        Returns
        -------
        AbstractTransform-like
            Initialized subclass (i.e., child) of `AbstractTransform`.

        Raises
        ------
        TypeError
            If `fnames` is not of type `str` or `iterable`.

        """
        workflow = CMPCCMaswWorkflow(cmpcc_strm=cmpcc_strm,sloc = sloc, rloc=rloc, dt=dt, settings=settings,
                            map_x=map_x, map_y=map_y)

        # Run and return.
        return workflow.run()

    @staticmethod
    def create_settings_dict(workflow="time-domain",
                             trim=False, trim_begin=0.0, trim_end=1.0,
                             mute=False, method="interactive",
                             window_kwargs=None, pad=False, df=1.0,
                             transform="fdbf", fmin=5, fmax=100, vmin=100,
                             vmax=1000, nvel=200, vspace="linear",
                             weighting="sqrt", steering="cylindrical",
                             snr=False, noise_begin=-0.5, noise_end=0.0,
                             signal_begin=0.0, signal_end=0.5,
                             pad_snr=True, df_snr=1.0, min_offset=0,
                             max_offset=np.inf):
        """Create settings `dict` using function arguments.

        See :meth:`Masw.create_settings_file` for details.

        """
        return {"workflow": str(workflow),
                "pre-processing": {
                    "trim": {
                        "apply": bool(trim),
                        "begin": float(trim_begin),
                        "end": float(trim_end)
                    },
                    "mute": {
                        "apply": bool(mute),
                        "method": str(method),
                        "window_kwargs": {} if window_kwargs is None else dict(window_kwargs)
                    },
                    "pad": {
                        "apply": bool(pad),
                        "df": float(df)
                    },
                    "offsets": {
                        "min": float(min_offset),
                        "max": float(max_offset),
                    }
        },
            "processing": {
                    "transform": str(transform),
                    "fmin": float(fmin),
                    "fmax": float(fmax),
                    "vmin": float(vmin),
                    "vmax": float(vmax),
                    "nvel": int(nvel),
                    "vspace": str(vspace),
                    "fdbf-specific": {
                        "weighting": str(weighting),
                        "steering": str(steering)
                    }
        },
            "signal-to-noise": {
                    "perform": bool(snr),
                    "noise": {
                        "begin": float(noise_begin),
                        "end": float(noise_end)
                    },
                    "signal": {
                        "begin": float(signal_begin),
                        "end": float(signal_end)
                    },
                    "pad": {
                        "apply": bool(pad_snr),
                        "df": float(df_snr)
                    }
        },
        }
