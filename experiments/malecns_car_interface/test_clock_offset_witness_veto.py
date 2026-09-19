import unittest
from clock_offset_witness_veto import WitnessVetoClockOffsetEstimator


def prefix_from_speed(speed):
    # Construct exact delta-v prefix under the Run-20 discrete convention.
    acc=[0.0]
    for i in range(1,len(speed)):
        acc.append((speed[i]-speed[i-1])/0.1)
    p=[0.0]
    for a in acc:p.append(p[-1]+a*0.1)
    return p

class WitnessVetoTests(unittest.TestCase):
    def feed(self, est, truth, reference):
        prefix=prefix_from_speed(truth)
        prev=None;obs=None
        for actual in range(10,110,5):
            reported=actual+3
            cur=(truth[actual],reported)
            if prev is not None:
                obs=est.observe_pair(previous_speed=prev[0],current_speed=cur[0],previous_reported_index=prev[1],current_reported_index=cur[1],imu_prefix_delta_v=prefix,reference_speed=reference,available_end_index=reported+8)
            prev=cur
        return obs
    def test_allows_offset_when_obd_witness_does_not_contradict(self):
        truth=[0.02*i*i+5 for i in range(140)]
        est=WitnessVetoClockOffsetEstimator()
        obs=self.feed(est,truth,truth)
        self.assertTrue(obs.active)
        self.assertEqual(obs.applied_offset_steps,3)
        self.assertFalse(obs.vetoed)
    def test_vetoes_when_obd_witness_supports_reported_time_instead(self):
        truth=[0.02*i*i+5 for i in range(140)]
        reference=[truth[max(0,i-3)] for i in range(140)]
        est=WitnessVetoClockOffsetEstimator()
        obs=self.feed(est,truth,reference)
        self.assertFalse(obs.active)
        self.assertTrue(obs.vetoed)
        self.assertLess(obs.reference_support_for_candidate,-0.08)
    def test_corrected_index_never_uses_future(self):
        est=WitnessVetoClockOffsetEstimator(applied_offset_steps=-4)
        self.assertEqual(est.corrected_index(20,18),18)

if __name__=='__main__':unittest.main()
