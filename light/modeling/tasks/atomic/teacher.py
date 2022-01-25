from parlai.core.teachers import ParlAIDialogTeacher
from parlai.core.loader import register_teacher
from light.constants import LIGHT_DATAPATH
from light.modeling.tasks.atomic.build import build
import copy
import os


def _path(opt):
    filname = "atomic_sample"

    opt["datatype"] = opt["datatype"].split(":")[0]

    if opt["datatype"] == "train":
        filname += "_train.txt"
    elif opt["datatype"] == "valid":
        filname += "_dev.txt"
    elif opt["datatype"] == "test":
        filname += "_test.txt"
    path = os.path.join(opt["light_datapath"], "atomic", opt["fill"], filname)
    return path


@register_teacher("light:atomic")
class AtomicTeacher(ParlAIDialogTeacher):
    def __init__(self, opt, shared=None):
        opt = copy.deepcopy(opt)
        opt["fill"] = "bert"  # TODO expose option for fill=rand
        build(opt)
        datafile = _path(opt)
        opt["parlaidialogteacher_datafile"] = datafile
        if shared is None:
            self._setup_data(datafile)
        self.id = datafile
        super().__init__(opt, shared)


class DefaultTeacher(AtomicTeacher):
    def __init__(self, opt, shared=None):
        opt["light_datapath"] = opt.get("light_datapath", LIGHT_DATAPATH)
        super().__init__(opt, shared)
