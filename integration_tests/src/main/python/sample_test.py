# Copyright (c) 2021, NVIDIA CORPORATION.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import pytest

from asserts import assert_gpu_and_cpu_are_equal_collect
from data_gen import *
from pyspark.sql.types import *

from marks import *

basic_gens = all_gen + [NullGen()]

# This is a conner case, use @ignore_order and "length = 4" to trigger
# If sample exec can't handle empty batch, will trigger "Input table cannot be empty" error
@ignore_order
@pytest.mark.parametrize('data_gen', [string_gen], ids=idfn)
def test_sample_produce_empty_batch(data_gen):
    assert_gpu_and_cpu_are_equal_collect(
        # length = 4 will generate empty batch after sample
        lambda spark: unary_op_df(spark, data_gen, length= 4).sample(fraction = 0.9, seed = 1)
    )

# the following cases is the normal cases and do not use @ignore_order
nested_gens = array_gens_sample + struct_gens_sample + map_gens_sample
@pytest.mark.parametrize('data_gen', basic_gens + nested_gens, ids=idfn)
def test_sample(data_gen):
    assert_gpu_and_cpu_are_equal_collect(
        lambda spark: unary_op_df(spark, data_gen).sample(fraction = 0.9, seed = 1),
        conf={'spark.sql.legacy.allowNegativeScaleOfDecimal': True}
    )

@pytest.mark.parametrize('data_gen', basic_gens + nested_gens, ids=idfn)
def test_sample_with_replacement(data_gen):
    assert_gpu_and_cpu_are_equal_collect(
        lambda spark: unary_op_df(spark, data_gen).sample(
            withReplacement =True, fraction = 0.5, seed = 1),
        conf={'spark.sql.legacy.allowNegativeScaleOfDecimal': True}
    )
