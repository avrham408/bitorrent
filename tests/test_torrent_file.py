import pytest
from collections import OrderedDict
from torrent.torrent_file import od_get_key, valid_torrent_path


#od_get_key
def test_od_get_key_functional():
    od = OrderedDict({'a':'b', (1, 2): 62233, "adar": ['java', 'disc']}) #OrderedDict data
    for key in od.keys():
        assert od_get_key(od, key) == od[key]


def test_od_get_key_error():
    od = OrderedDict({'a':'b', (1, 2): 62233, "adar": ['java', 'disc']}) #OrderedDict data
    #mandat = True
    with pytest.raises(KeyError):
        od_get_key(od, 'c', True)
    with pytest.raises(KeyError):
        od_get_key(od, (1,3), True)
    with pytest.raises(TypeError):
        od_get_key(od, ['a'], True)
    #no mandat
    assert od_get_key(od, ['a']) == None 
    assert od_get_key(od, (1,3)) == None 
    assert od_get_key(od, 'c') == None
    #mandat == False
    assert od_get_key(od, ['a'], False) == None 
    assert od_get_key(od, (1,3), False) == None 
    assert od_get_key(od, 'c', False) == None


def test_od_get_key_bed_types():
    test_dict = {'a':'b', (1, 2): 62233, "adar": ['java', 'disc']}
    #n
    with pytest.raises(TypeError):
        od_get_key(test_dict, 'a', True)
    od = OrderedDict(test_dict) #OrderedDict data
    #not enough variables
    with pytest.raises(TypeError):
        od_get_key(od)

def test_valid_torrent_file_not_exist():
    pass
    
if __name__ == "__main__":
    test_od_get_key_error()
