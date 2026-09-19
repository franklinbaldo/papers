"""Reality-bounded cross-witness guard for clock-offset repair.

The existing phone-IMU estimator proposes a GNSS clock repair. An independent
OBD-II speed-delta witness may veto that proposal when the proposed shift makes
GNSS delta-speed materially less consistent with OBD history than leaving the
clock unshifted. This is a safety guard, not a second requirement to prove the
offset, so a noisy OBD witness does not automatically suppress an otherwise
supported IMU repair.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from clock_offset_estimation import _huber_loss, speed_interval_delta_v

@dataclass(frozen=True)
class WitnessOffsetObservation:
    applied_offset_steps:int
    candidate_offset_steps:int
    relative_gain_over_zero:float
    reference_support_for_candidate:float
    reference_candidate_offset_steps:int
    vetoed:bool
    active:bool
    pairs_used:int

@dataclass
class WitnessVetoClockOffsetEstimator:
    max_offset_steps:int=6
    window_pairs:int=40
    min_pairs:int=8
    imu_huber_delta_v:float=.55
    reference_huber_delta_v:float=.70
    min_abs_offset_steps:int=2
    min_relative_gain:float=.08
    max_reference_contradiction:float=.08
    applied_offset_steps:int=0
    candidate_offset_steps:int=0
    relative_gain_over_zero:float=0.0
    reference_support_for_candidate:float=0.0
    reference_candidate_offset_steps:int=0
    vetoed:bool=False
    _pairs:list[tuple[float,float,int,int]]=field(default_factory=list)
    def observe_pair(self,*,previous_speed:float,current_speed:float,previous_reported_index:int,current_reported_index:int,imu_prefix_delta_v:list[float],reference_speed:list[float],available_end_index:int)->WitnessOffsetObservation:
        if current_reported_index<=previous_reported_index:return self.observation()
        self._pairs.append((previous_speed,current_speed,previous_reported_index,current_reported_index))
        if len(self._pairs)>self.window_pairs:self._pairs=self._pairs[-self.window_pairs:]
        if len(self._pairs)<self.min_pairs:return self.observation()
        iloss={};rloss={};counts={}
        for off in range(-self.max_offset_steps,self.max_offset_steps+1):
            il=[];rl=[]
            for ps,cs,pr,cr in self._pairs:
                s=pr-off;e=cr-off
                if s<0 or e<=s or e>available_end_index or e>=len(reference_speed) or e+1>=len(imu_prefix_delta_v):continue
                d=cs-ps
                il.append(_huber_loss(d-speed_interval_delta_v(imu_prefix_delta_v,s,e),self.imu_huber_delta_v))
                rl.append(_huber_loss(d-(reference_speed[e]-reference_speed[s]),self.reference_huber_delta_v))
            if len(il)>=self.min_pairs:
                iloss[off]=sum(il)/len(il);rloss[off]=sum(rl)/len(rl);counts[off]=len(il)
        if 0 not in iloss:return self.observation()
        best=min(iloss,key=lambda o:(iloss[o],abs(o-self.candidate_offset_steps),abs(o)))
        iz=max(iloss[0],1e-12);gain=max(0.0,(iz-iloss[best])/iz)
        rz=max(rloss[0],1e-12)
        reference_support=(rz-rloss[best])/rz if best in rloss else -1.0
        ref_best=min(rloss,key=lambda o:(rloss[o],abs(o-self.reference_candidate_offset_steps),abs(o)))
        base_active=abs(best)>=self.min_abs_offset_steps and gain>=self.min_relative_gain
        veto=base_active and reference_support < -self.max_reference_contradiction
        self.candidate_offset_steps=best;self.relative_gain_over_zero=gain;self.reference_support_for_candidate=reference_support;self.reference_candidate_offset_steps=ref_best;self.vetoed=veto
        self.applied_offset_steps=best if base_active and not veto else 0
        return WitnessOffsetObservation(self.applied_offset_steps,best,gain,reference_support,ref_best,veto,self.applied_offset_steps!=0,counts.get(best,0))
    def corrected_index(self,reported_index:int,available_end_index:int)->int:return max(0,min(available_end_index,reported_index-self.applied_offset_steps))
    def observation(self)->WitnessOffsetObservation:return WitnessOffsetObservation(self.applied_offset_steps,self.candidate_offset_steps,self.relative_gain_over_zero,self.reference_support_for_candidate,self.reference_candidate_offset_steps,self.vetoed,self.applied_offset_steps!=0,min(len(self._pairs),self.window_pairs))
