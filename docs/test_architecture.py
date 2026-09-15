"""Negative controls for the profile's source and projection contract."""
import copy
import unittest
import build_architecture as b

class ArchitectureContractTests(unittest.TestCase):
    def setUp(self):
        self.f=b.load(b.ROOT/'docs/facts.json'); self.ir=b.load(b.ROOT/'docs/architecture.json')
    def rejected(self):
        with self.assertRaises((ValueError,KeyError)):
            b.verify(self.f,self.ir)
    def test_current_facts_and_projection(self): self.assertTrue(b.verify()['ok'])
    def test_hash_tampering_rejected(self):
        self.f['components'][0]['evidence'][0]['excerpt_sha256']='0'*64;self.rejected()
    def test_missing_evidence_rejected(self):
        self.f['components'][0]['evidence']=[];self.rejected()
    def test_self_certification_rejected(self):
        self.f['components'][0]['evidence'][0]['path']='docs/index.html';self.rejected()
    def test_inference_without_independent_paths_rejected(self):
        item=next(x for x in self.f['relations'] if x['basis']=='inferred');item['evidence']=item['evidence'][:1];self.rejected()
    def test_id_drift_rejected(self):
        self.ir['components'][0]['id']='another-agent';self.rejected()
    def test_direction_drift_rejected(self):
        e=self.ir['connections'][0];e['from'],e['to']=e['to'],e['from'];self.rejected()
    def test_invented_component_rejected(self):
        self.ir['components'].append(copy.deepcopy(self.ir['components'][0]));self.rejected()
    def test_unknown_relation_endpoint_rejected(self):
        self.f['relations'][0]['to']='missing-node';self.rejected()
    def test_invented_boundary_rejected(self):
        self.ir['boundaries']=[{'kind':'region','label':'Invented deployment','wraps':['agents']}];self.rejected()
    def test_source_pin_drift_rejected(self):
        self.ir['meta']['repository']['revision']='0'*40;self.rejected()
    def test_readme_has_requested_output_path(self):
        self.assertIn('](docs/index.html)',(b.ROOT/'README.md').read_text())

if __name__=='__main__': unittest.main()
