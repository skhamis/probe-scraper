# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import tempfile
import os
import json

import scraper
from parsers.histograms import HistogramsParser
import transform_revisions
import transform_probes


class DummyParser:
    def parse(self, files):
        return {}

PARSERS = {
    # This lists the available probe registry parsers:
    # parser type -> parser
    'histograms': HistogramsParser(),
    'scalars': DummyParser(),
    'events': DummyParser(),
}


def main(target_dir = tempfile.mkdtemp()):
    # Scrape probe data from repositories.
    nodes = scraper.scrape(target_dir)

    # Parse probe data from files.
    probes = {
        # node_id -> {
        #   histograms: {
        #     name: ...,
        #     ...
        #   },
        #   scalars: {
        #     ...
        #   },
        # }
    }
    def add_probe_data(node_id, probe_type, probe_data):
        if not node_id in probes:
            probes[node_id] = {}
        probes[node_id][probe_type] = probe_data

    for node_id,details in nodes.iteritems():
        for probe_type,paths in details['registries'].iteritems():
            probe_data = PARSERS[probe_type].parse(paths)
            add_probe_data(node_id, probe_type, probe_data)

    # Transform extracted data.
    revisions = transform_revisions.transform(nodes)
    probe_data = transform_probes.transform(probes, nodes)

    def dump_json(data, file_name):
        with open(os.path.join(target_dir, file_name), 'w') as f:
            json.dump(data, f, sort_keys=True, indent=2)

    dump_json(revisions, 'revisions.json')

if __name__ == "__main__":
    main('_tmp')
