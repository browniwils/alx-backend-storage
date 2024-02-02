#!/usr/bin/env python3
"""Module to update document in monogodb."""


def update_topics(mongo_collection, name, topics):
    """updates all topics of a collection's document based on the name."""

    mongo_collection.update_many(
        {'name': name},
        {'$set': {'topics': topics}}
    )
