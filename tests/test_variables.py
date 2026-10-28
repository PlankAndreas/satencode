from satencode import Variables


def test_variable_numbering():

    vm = Variables()

    x = vm.new("x", range(3), range(2))

    assert x[0,0] == 1
    assert x[0,1] == 2
    assert x[1,0] == 3
    assert x[2,1] == 6

    loc = vm.new("location", range(2), range(3), range(2))

    assert loc[1,2,0] == 17
    assert loc[1,2,1] == 18