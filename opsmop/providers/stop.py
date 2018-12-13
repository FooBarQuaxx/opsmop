# Copyright 2018 Michael DeHaan LLC, <michael@michaeldehaan.net>
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from opsmop.providers.provider import Provider

class Stop(Provider):

    def quiet(self):
        # silence most callbacks
        return True

    def plan(self):
        self.needs('stop')

    def skip_plan_stage(self):
        return True

    def apply(self):
        
        self.do('stop')
        return self.fatal(self.msg)
