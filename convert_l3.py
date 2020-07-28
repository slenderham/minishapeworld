"""
Convert to L3 format
"""

import numpy as np
import os
import json


def preprocess_hints(hints):
    hints = list(hints)
    return hints

def preprocess_worlds(world):
    data = json.load(world);
    objects = [];
    for concept in data:
        objects.append([]);
        for inst in concept:
            objects[-1].append([]);
            for shape in inst['shapes']:
                objects[-1][-1].append([shape['color'] + ' ' + shape['shape'], [shape['pos']['x']/10.0-3.2, shape['pos']['y']/10.0-3.2]]);
    return objects

if __name__ == '__main__':
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

    parser = ArgumentParser(
        description=__doc__,
        formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument('--dataset', default='./l3', help='Dataset to load')
    parser.add_argument('--save_dir', default='./shapeworld', help='Directory to save to')

    args = parser.parse_args()

    os.makedirs(args.save_dir, exist_ok=True)

    for split in ['train', 'val', 'val_same', 'test', 'test_same']:
        print(split)
        fname = os.path.join(args.dataset, f"{split}.npz")
        data = np.load(fname)
        # Positive examples: first 4
        n_shot = data['imgs'].shape[1] - 1
        examples = data['imgs'][:, :n_shot]
        examples = np.transpose(examples, (0, 1, 3, 4, 2))  # CHW -> HWC
        inputs = data['imgs'][:, -1]
        inputs = np.transpose(inputs, (0, 2, 3, 1))
        hints = preprocess_hints(data['langs'])
        labels = data['labels'][:, -1]
        assert np.all(data['labels'][:, :n_shot] == 1)

        # Convert to floats
        examples = examples.astype(np.float32) / 255.0
        inputs = inputs.astype(np.float32) / 255.0
        labels = labels.astype(np.float32)

        split_dir = os.path.join(args.save_dir, split)
        os.makedirs(split_dir, exist_ok=True)

        examples_fname = os.path.join(split_dir, 'examples.npz')
        np.savez(examples_fname, examples)

        inputs_fname = os.path.join(split_dir, 'inputs.npz')
        np.savez(inputs_fname, inputs)

        hints_fname = os.path.join(split_dir, 'hints.json')
        with open(hints_fname, 'w') as f:
            json.dump(hints, f)
        
        labels_fname = os.path.join(split_dir, 'labels.npz')
        np.savez(labels_fname, labels)

        world_fname = os.path.join(args.dataset, f"{split}_worlds.json")
        with open(world_fname, 'r') as f:
            list_of_objects = preprocess_worlds(f);
        world_new_fname = os.path.join(split_dir, 'worlds.json')
        with open(world_new_fname, 'w') as f:
            json.dump(list_of_objects, f);