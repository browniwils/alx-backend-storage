#!/usr/bin/env python3
"""Module for updating document in mongodb."""


def schools_by_topic(mongo_collection, topic):
    """Get list of school having a specific topic."""

    topic_filter = {
        'topics': {
            '$elemMatch': {
                '$eq': topic,
            },
        },
    }
    return [document for document in mongo_collection.find(topic_filter)]
