#include <cstdint>

/**
* Enum Mercury.EScoreGenre
*/
enum class Mercury_EScoreGenre : uint8_t
{
    EScoreGenre__INVALID         = 0,
    EScoreGenre__GENRE_ANIME     = 1,
    EScoreGenre__GENRE_VOCALOID  = 2,
    EScoreGenre__GENRE_TOHO      = 3,
    EScoreGenre__GENRE_25D       = 4,
    EScoreGenre__GENRE_VARIETY   = 5,
    EScoreGenre__GENRE_ORIGINAL  = 6,
    EScoreGenre__GENRE_HARDCORE  = 7,
    EScoreGenre__GENRE_VTUBER    = 8,
    EScoreGenre__NUM             = 9,
    EScoreGenre__EScoreGenre_MAX = 10
};

// note: enum starts at -1