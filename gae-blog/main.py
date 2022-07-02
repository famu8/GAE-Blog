# Copyright 2022 NoCommandLine
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
# [START gae_python37_app]

import argparse
import gae_blog

# This method allows you to run the App via Flask by calling python main.py
# or by using dev_appserver.py
if __name__ == '__main__':
     # Executed if you run 'python main.py'
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default="8080")
    parser.add_argument('--host', default="127.0.0.1")
    args = vars(parser.parse_args())
    app = gae_blog.create_app()
    app.run(host=args["host"], port=args["port"], debug=True)

else:
    app = gae_blog.create_app()

# [END gae_python37_app]