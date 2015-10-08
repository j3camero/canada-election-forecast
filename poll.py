import datetime

class Poll(object):

    def __init__(self, date, sample_size, riding_number, riding_name):
        """Sets up a new poll object."""
        self.party_support = {}
        self.date = date
        self.sample_size = sample_size
        self.riding_number = riding_number
        self.riding_name = riding_name

    def CalculateRawWeight(self, current_date=datetime.datetime.now()):
        """Calculates a weight for mixing polls from multiple sources."""
        age_seconds = (current_date - self.date).total_seconds()
        age_days = float(age_seconds) / (24 * 3600)
        age_years = age_days / 365.25
        return self.sample_size * (0.25 ** age_years)

    def Copy(self):
        """Makes a deep copy of this poll object."""
        poll = Poll(self.date, self.sample_size, self.riding_number,
                    self.riding_name)
        for party, support in self.party_support.items():
            poll.party_support[party] = support
        return poll

    def NormalizeInPlace(self):
        """Normalize in-place so all party support adds to 1."""
        divisor = sum(self.party_support.values())
        for party in self.party_support:
            self.party_support[party] /= divisor

    def CopyAndNormalize(self):
        """Returns a normalized poll whose numbers sum to 1."""
        poll = self.Copy()
        poll.NormalizeInPlace()
        return poll
