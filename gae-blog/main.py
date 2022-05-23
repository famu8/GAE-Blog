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

import gae_blog

# This method allows you to run the App via Flask by calling python main.py
# or by using dev_appserver.py
if __name__ == '__main__':
    app = gae_blog.create_app()
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=57080, debug=True)

else:
    app = gae_blog.create_app()

# [END gae_python37_app]