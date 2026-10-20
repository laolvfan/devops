"""Team E7 regression: reject a replacement final stage before building.

Requires the E6 implementation of draft.autobuild. During E7 preparation this
test is checked against the separately recorded teaching reference.
"""
import unittest

from draft.autobuild import prepare_candidate


class TeamCandidateTests(unittest.TestCase):
    def test_multistage_candidate_is_rejected(self):
        broken = (
            "FROM python:3.13-slim\n"
            "WORKDIR /work\n"
            "COPY main.c Makefile ./\n"
            "RUN make\n"
            'CMD ["./hello"]\n'
        )
        candidate = (
            "FROM python:3.13-slim@sha256:" + "a" * 64 + "\n"
            "WORKDIR /work\n"
            "COPY main.c Makefile ./\n"
            "RUN apt-get update && apt-get install -y build-essential\n"
            "RUN make\n"
            'CMD ["./hello"]\n'
            "FROM busybox:1.37\n"
            'CMD ["echo", "hello E3"]\n'
        )
        with self.assertRaises(ValueError):
            prepare_candidate(broken, candidate)


if __name__ == "__main__":
    unittest.main()
