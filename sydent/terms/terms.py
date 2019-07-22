# -*- coding: utf-8 -*-

# Copyright 2019 The Matrix.org Foundation C.I.C.
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

import logging
import yaml


logger = logging.getLogger(__name__)


class Terms(object):
    def __init__(self, yamlObj):
        self._rawTerms = yamlObj

    def getMasterVersion(self):
        return self._rawTerms['master_version']

    def getForClient(self):
        policies = {}
        for docName, doc in self._rawTerms['docs'].items():
            policies[docName] = {
                'version': doc['version'],
            }
            for langName, lang in doc['langs'].items():
                policies[docName][langName] = lang
        return { 'policies': policies }

    def getUrlSet(self):
        urls = set()
        for docName, doc in self._rawTerms['docs'].items():
            for langName, lang in doc['langs'].items():
                urls.add(lang['url'])
        return urls

    def urlListIsSufficient(self, urls):
        agreed = set()
        urlset = set(urls)

        for docName, doc in self._rawTerms['docs'].items():
            for _, lang in doc['langs'].items():
                if lang['url'] in urlset:
                    agreed.add(docName)
                    break

        required = set(self._rawTerms['docs'].keys())
        return agreed == required

def get_terms(sydent):
    try:
        termsYaml = None
        with open(sydent.cfg.get('general', 'terms.path')) as fp:
            termsYaml = yaml.full_load(fp)
        if 'master_version' not in termsYaml:
            raise Exception("No master version")
        if 'docs' not in termsYaml:
            raise Exception("No 'docs' key in terms")
        for docName, doc in termsYaml['docs'].items():
            if 'version' not in doc:
                raise Exception("'%s' has no version" % (docName,))
            if 'langs' not in doc:
                raise Exception("'%s' has no langs" % (docName,))
            for langKey, lang in doc['langs'].items():
                if 'name' not in lang:
                    raise Exception("lang '%s' of doc %s has no name" % (langKey, docName))
                if 'url' not in lang:
                    raise Exception("lang '%s' of doc %s has no url" % (langKey, docName))

        return Terms(termsYaml)
    except Exception:
        logger.exception("Couldn't read terms file '%s'", sydent.cfg.get('general', 'terms.path'))
