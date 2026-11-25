"""Proposed source-claim semantics, not a support certificate or access policy."""
from dataclasses import dataclass

VERSION='source-claim-frame-v1'

@dataclass(frozen=True)
class ClaimFrame:
    actor: str
    action: str
    object_text: str
    negative: bool=False
    modality: str='assertion'
    conditions: tuple=()
    task_actor: str=''
    content_negative: bool=False
    time_text: str=''

    @classmethod
    def from_action(cls,value):
        return cls(value['actor_text'],value['action'],value['object_text'],
                   value['negative'],time_text=value.get('temporal_qualification_text',''))
