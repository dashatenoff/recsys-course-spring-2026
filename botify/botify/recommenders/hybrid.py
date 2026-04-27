from .recommender import Recommender


class HybridRecommender(Recommender):
    def __init__(self, indexed, i2i, fallback, catalog):
        self.indexed = indexed              # user-based
        self.i2i = i2i                      # item-based
        self.fallback = fallback
        self.catalog = catalog

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:

        # USER RECS (главный список вкуса)
        user_bytes = self.indexed.recommendations_redis.get(user)

        if user_bytes is None:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        user_list = list(self.catalog.from_bytes(user_bytes))

        # I2I RECS (intent)
        if prev_track is not None:
            i2i_bytes = self.i2i.i2i_redis.get(prev_track)

            if i2i_bytes is not None:
                i2i_list = list(self.catalog.from_bytes(i2i_bytes))

                # ПЕРЕСЕЧЕНИЕ (ключ)
                i2i_set = set(i2i_list[:50])  # ускоряем поиск

                for track in user_list[:20]:  # усиливаем топ user
                    if track in i2i_set:
                        return track

        #fallback  лучший user track
        return user_list[0]