import pytest
import uuid
from data_lineage.bloomfilter.Bloomfilter import BloomFilter

@pytest.fixture
def bloom_filter():
    return {
        'sm_bf': BloomFilter(size=64, hash_count=8),
        'md_bf': BloomFilter(size=256, hash_count=8),
        'lg_bf': BloomFilter(size=1024, hash_count=8),
        'xl_bf': BloomFilter(size=16384, hash_count=8)
    }

@pytest.mark.parametrize('bf_size', ['sm_bf', 'md_bf', 'lg_bf', 'xl_bf'])
def test_add_and_contains(bloom_filter, bf_size):
    bf = bloom_filter[bf_size]
    elements = ['test', 'hello', 'world', 'python!']

    for element in elements:
        bf.hash(element)
        assert bf.contains(element)

@pytest.mark.parametrize('bf_size', ['sm_bf', 'md_bf', 'lg_bf', 'xl_bf'])
def test_does_not_contain(bloom_filter, bf_size):
    bf = bloom_filter[bf_size]
    elements = ['entropy', 'extemporize', 'incorporeal', 'egress']

    bf.hash('hello')

    for element in elements:
        assert not bf.contains(element)

        bf.hash(element)
        assert bf.contains(element)

@pytest.mark.parametrize('bf_size', ['sm_bf', 'md_bf', 'lg_bf', 'xl_bf'])
def test_collision_handling(bloom_filter, bf_size):
    bf = bloom_filter[bf_size]
    elements = ['test', 'aaa', 'abc', 'hello']
    collisions = ['testt1', 'aaaa', 'cba', ' hello 0']
    for element in elements:
        bf.hash(element)

    for collision in collisions:
        assert not bf.contains(collision), f"False positive detected for element: {collision}"

@pytest.mark.parametrize('bf_size', ['sm_bf', 'md_bf', 'lg_bf', 'xl_bf'])
def test_collision_distance(bloom_filter, bf_size):
    bf = bloom_filter[bf_size]
    iterations = 0

    while(1):
        unique_string = uuid.uuid4().hex[:16].upper()
        if bf.contains(unique_string):
            break
        else:
            iterations += 1
            bf.hash(unique_string)

    print(f'Number of iterations before a collision occurs for {bf_size}: {iterations}')
    assert iterations > 0
