"""Run 21: falsify IMU-only clock repair and test an independent OBD witness veto.

Synthetic truth and actual GNSS measurement time are retained only by the
harness for scoring. Deployable estimators receive GNSS speed/report time,
phone IMU, OBD-II speed history, and the arrival boundary. The experiment
stresses phone-IMU bias, axis-scale error, gravity leakage, and clipping.
"""
from __future__ import annotations
import argparse, json, math, random, statistics
from dataclasses import dataclass
from clock_offset_estimation import RobustClockOffsetEstimator
from clock_offset_witness_veto import WitnessVetoClockOffsetEstimator
DT=0.1

@dataclass(frozen=True)
class Fix:
    reported_index:int
    arrival_index:int
    value:float
    _actual_index_for_scoring:int
@dataclass
class Episode:
    truth:list[float]; obd:list[float]; imu:list[float]; arrivals:dict[int,list[Fix]]

def generate_episode(seed:int,*,clock_mode:str,obd_mode:str,imu_mode:str,steps:int=300,dropout:float=0.15)->Episode:
    rng=random.Random(seed);truth=[];acc=[];speed=rng.uniform(8,25);a=rng.uniform(-.5,.5)
    for _ in range(steps):
        impulse=rng.gauss(0,.55)
        if rng.random()<.08:impulse+=rng.uniform(-2.5,2.5)
        a=max(-4,min(3.5,.90*a+impulse));speed=max(0,speed+a*DT);truth.append(speed);acc.append(a)
    bias=[0.0]*steps
    if obd_mode=='static':
        b=rng.choice((-1,1))*rng.uniform(1,2);bias=[b]*steps
    elif obd_mode=='drift':
        b=rng.uniform(-.3,.3)
        for i in range(steps):b=max(-2,min(2,b+rng.gauss(0,.025)));bias[i]=b
    elif obd_mode!='clean':raise ValueError(obd_mode)
    obd=[truth[i]+bias[i]+rng.gauss(0,.18) for i in range(steps)]
    base_bias=rng.gauss(0,.06)
    phase=rng.uniform(0,2*math.pi)
    scale=rng.choice((.65,1.35))
    extra_bias=rng.choice((-1,1))*.60
    imu=[]
    for i,x in enumerate(acc):
        value=x+base_bias+rng.gauss(0,.22)
        if imu_mode=='bias':value+=extra_bias
        elif imu_mode=='scale':value=scale*x+base_bias+rng.gauss(0,.22)
        elif imu_mode=='gravity':value+=.80*math.sin(2*math.pi*i*DT/8.0+phase)
        elif imu_mode=='clip':value=max(-.8,min(.8,value))
        elif imu_mode!='clean':raise ValueError(imu_mode)
        imu.append(value)
    if clock_mode not in {'clean','offset','offset_jitter'}:raise ValueError(clock_mode)
    base=3 if clock_mode!='clean' else 0
    arrivals={}
    for actual in range(0,steps,5):
        if rng.random()<dropout:continue
        jitter=rng.randint(-2,2) if clock_mode=='offset_jitter' else 0
        reported=max(0,min(steps-1,actual+base+jitter));arrival=actual+rng.randint(4,12)
        if arrival>=steps:continue
        arrivals.setdefault(arrival,[]).append(Fix(reported,arrival,truth[actual]+rng.gauss(0,.45),actual))
    return Episode(truth,obd,imu,arrivals)

def mean(xs):return statistics.mean(xs) if xs else 0.0

def run_episode(ep:Episode)->dict[str,float]:
    prefix=[0.0]
    for x in ep.imu:prefix.append(prefix[-1]+x*DT)
    imu_est=RobustClockOffsetEstimator();guard=WitnessVetoClockOffsetEstimator()
    prev=None
    metrics={k:[] for k in ['raw_time_error','imu_time_error','witness_veto_time_error','raw_reference_error','imu_reference_error','witness_veto_reference_error','imu_active','witness_veto_active','witness_veto_fraction']}
    for arrival in range(len(ep.truth)):
        for fix in ep.arrivals.get(arrival,[]):
            if prev is not None and fix.reported_index>prev.reported_index:
                io=imu_est.observe_pair(previous_speed=prev.value,current_speed=fix.value,previous_reported_index=prev.reported_index,current_reported_index=fix.reported_index,imu_prefix_delta_v=prefix,available_end_index=arrival)
                go=guard.observe_pair(previous_speed=prev.value,current_speed=fix.value,previous_reported_index=prev.reported_index,current_reported_index=fix.reported_index,imu_prefix_delta_v=prefix,reference_speed=ep.obd,available_end_index=arrival)
            else:
                io=imu_est.observation();go=guard.observation()
            prev=fix
            raw=max(0,min(arrival,fix.reported_index));ic=imu_est.corrected_index(fix.reported_index,arrival);cc=guard.corrected_index(fix.reported_index,arrival)
            actual=fix._actual_index_for_scoring
            metrics['raw_time_error'].append(abs(raw-actual));metrics['imu_time_error'].append(abs(ic-actual));metrics['witness_veto_time_error'].append(abs(cc-actual))
            metrics['raw_reference_error'].append(abs(ep.obd[raw]-ep.truth[actual]));metrics['imu_reference_error'].append(abs(ep.obd[ic]-ep.truth[actual]));metrics['witness_veto_reference_error'].append(abs(ep.obd[cc]-ep.truth[actual]))
            metrics['imu_active'].append(1.0 if io.active else 0.0);metrics['witness_veto_active'].append(1.0 if go.active else 0.0);metrics['witness_veto_fraction'].append(1.0 if go.vetoed else 0.0)
    return {k:mean(v) for k,v in metrics.items()}

def evaluate(*,seeds:int=3,episodes_per_seed:int=25,steps:int=300)->dict[str,object]:
    out={'config':{'seeds':seeds,'episodes_per_seed':episodes_per_seed,'steps':steps,'dt_s':DT,'obd_hz':10,'gnss_hz':2,'gnss_dropout':.15,'gnss_delay_s':[.4,1.2],'offset_s':.3,'jitter_s':[-.2,.2],'imu_stresses':{'bias_mps2':.60,'scale':[.65,1.35],'gravity_leak_amplitude_mps2':.80,'clip_mps2':[-.8,.8]}},'regimes':{}}
    for obd_i,obd in enumerate(('clean','static','drift')):
        out['regimes'][obd]={}
        for clk_i,clk in enumerate(('clean','offset','offset_jitter')):
            out['regimes'][obd][clk]={}
            for imu_i,imu in enumerate(('clean','bias','scale','gravity','clip')):
                rows=[]
                for s in range(seeds):
                    episodes=[]
                    for e in range(episodes_per_seed):
                        seed=2_100_000+obd_i*500_000+clk_i*100_000+imu_i*20_000+s*2_000+e
                        episodes.append(run_episode(generate_episode(seed,clock_mode=clk,obd_mode=obd,imu_mode=imu,steps=steps)))
                    rows.append({k:statistics.mean(r[k] for r in episodes) for k in episodes[0]})
                out['regimes'][obd][clk][imu]={k:{'mean':statistics.mean(r[k] for r in rows),'sd_across_seeds':statistics.stdev(r[k] for r in rows) if len(rows) > 1 else 0.0} for k in rows[0]}
    return out

def main():
    p=argparse.ArgumentParser();p.add_argument('--seeds',type=int,default=3);p.add_argument('--episodes-per-seed',type=int,default=25);p.add_argument('--steps',type=int,default=300);a=p.parse_args();print(json.dumps(evaluate(seeds=a.seeds,episodes_per_seed=a.episodes_per_seed,steps=a.steps),indent=2,sort_keys=True))
if __name__=='__main__':main()
