#!/usr/bin/env python3
"""Module for logging stats."""

from pymongo import MongoClient


def print_nginx_request_logs(nginx_collection):
    """Prints stats about Nginx request logs."""

    print(f"{nginx_collection.count_documents({})} logs")
    print("Methods:")
    methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]
    for method in methods:
        count_req = len(list(nginx_collection.find({"method": method})))
        print(f"\tmethod {method}: {count_req}")
    count_status_check = len(list(
        nginx_collection.find({"method": "GET", "path": "/status"})
    ))
    print(f"{count_status_check} status check")


def run():
    """Provides some stats about Nginx logs stored in MongoDB."""

    client = MongoClient("mongodb://127.0.0.1:27017")
    print_nginx_request_logs(client.logs.nginx)


if __name__ == "__main__":
    run()
