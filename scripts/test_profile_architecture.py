import copy
import unittest
from verify_profile_architecture import ROOT,check,load,safe_path

class ProfileArchitectureTests(unittest.TestCase):
    def setUp(self):
        self.facts=load(ROOT/'docs/facts.json')
        self.ir=load(ROOT/'docs/index.json')
    def test_committed_candidate(self):
        self.assertTrue(check(ROOT)['ok'])
    def test_source_hash_tamper(self):
        self.facts['components'][0]['evidence'][0]['excerpt_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'hash mismatch'):check(ROOT,self.facts,self.ir)
    def test_projection_tamper(self):
        self.ir['components'][0]['label']='invented'
        with self.assertRaisesRegex(ValueError,'projection drift'):check(ROOT,self.facts,self.ir)
    def test_invented_edge(self):
        self.ir['connections'].append(dict(self.ir['connections'][0],id='invented'))
        with self.assertRaisesRegex(ValueError,'projection drift'):check(ROOT,self.facts,self.ir)
    def test_self_citation(self):
        self.facts['components'][0]['evidence'][0]['path']='docs/index.html'
        with self.assertRaisesRegex(ValueError,'self-generated'):check(ROOT,self.facts,self.ir)
    def test_quality_downgrade(self):
        self.ir['meta']['quality_profile']='standard'
        with self.assertRaisesRegex(ValueError,'showcase'):check(ROOT,self.facts,self.ir)
    def test_path_escape(self):
        for path in ('../secret','/etc/passwd','docs/../README.md'):
            with self.assertRaises(ValueError):safe_path(path)
    def test_unpinned_revision(self):
        self.facts['repository']['revision']='main'
        with self.assertRaisesRegex(ValueError,'unpinned'):check(ROOT,self.facts,self.ir)
    def test_unknown_schema_key(self):
        self.facts['new_semantics']={}
        with self.assertRaisesRegex(ValueError,'schema keys'):check(ROOT,self.facts,self.ir)
    def test_basis_cannot_be_promoted(self):
        self.facts['components'][0]['basis']='observed'
        with self.assertRaisesRegex(ValueError,'declared facts only'):check(ROOT,self.facts,self.ir)
    def test_duplicate_component(self):
        self.facts['components'].append(copy.deepcopy(self.facts['components'][0]))
        with self.assertRaisesRegex(ValueError,'unique and sorted'):check(ROOT,self.facts,self.ir)

if __name__=='__main__':unittest.main()
