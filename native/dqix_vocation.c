/* DQIX-Coop-Edition: experimental native starting-vocation save hook.
 * Original implementation. No commercial game code or data included.
 *
 * Called only at save-chip startup, before the game reads the save.
 * The caller decides when to opt in; absent opt-in, this is inert.
 */
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#define DQIX_SLOT_SIZE 32768u
#define DQIX_SAVE_SIZE 65536u
#define DQIX_HERO_BASE 136u
#define DQIX_HERO_SIZE 572u
#define DQIX_HERO_VOCATION 80u
#define DQIX_HERO_LEVELS 2u
#define DQIX_HERO_EXPS 28u
#define DQIX_STANDBY 7572u
#define DQIX_PARTY 7577u
#define DQIX_PRESENT 21u

static uint32_t dqix_read32(const unsigned char* p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8)
        | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}
static void dqix_write32(unsigned char* p, uint32_t v) {
    p[0] = (unsigned char)v; p[1] = (unsigned char)(v >> 8);
    p[2] = (unsigned char)(v >> 16); p[3] = (unsigned char)(v >> 24);
}
static uint32_t dqix_crc32(const unsigned char* p, size_t n) {
    uint32_t c = 0xFFFFFFFFu;
    for (size_t i = 0; i < n; ++i) {
        c ^= p[i];
        for (int j = 0; j < 8; ++j)
            c = (c >> 1) ^ (0xEDB88320u & (0u - (c & 1u)));
    }
    return ~c;
}
static int dqix_checks_ok(const unsigned char* b) {
    static const size_t ck[3][3] = {{16,20,36},{36,40,132},{132,136,28644}};
    if (memcmp(b, "DRAGON QUEST IX", 15) != 0) return 0;
    for (int k = 0; k < 3; ++k) {
        const size_t* a = ck[k];
        if (dqix_read32(b + a[0]) != dqix_crc32(b + a[1], a[2] - a[1]))
            return 0;
    }
    return 1;
}
static int dqix_vocation_id(const char* name) {
    if (!name) return 0;
    if (strcmp(name,"warrior") == 0) return 1;
    if (strcmp(name,"priest") == 0) return 2;
    if (strcmp(name,"mage") == 0) return 3;
    if (strcmp(name,"martial-artist") == 0) return 4;
    if (strcmp(name,"thief") == 0) return 5;
    return 0;
}

/* Return 1 when both slots were patched, 0 when disabled, -1 if rejected.
 * When rejected, the input buffer is not modified at all.
 *
 * This intentionally requires both occupied slots to represent untouched
 * level-1 Minstrels (0 or 7 EXP, matching the currently tested opening).
 * Existing characters, blank saves, unexpected save layouts, and nonmatching
 * alternate slots are refused. Only the current-vocation byte and the
 * corresponding checksum are changed, in BOTH valid slots.
 */
int dqix_apply_start_vocation(unsigned char* image, size_t size,
                              const char* requested) {
    if (!requested || !*requested) return 0;
    int target = dqix_vocation_id(requested);
    if (!image || size != DQIX_SAVE_SIZE || !target) return -1;

    size_t vocation_offsets[2];
    for (int slot = 0; slot < 2; ++slot) {
        const size_t base = (size_t)slot * DQIX_SLOT_SIZE;
        const unsigned char* b = image + base;
        if (!(b[DQIX_PRESENT] & 1u) || !dqix_checks_ok(b)) return -1;
        unsigned int standby = b[DQIX_STANDBY], party = b[DQIX_PARTY];
        if (standby > 8 || party != 1 || standby + party > 13) return -1;
        size_t hero = DQIX_HERO_BASE + standby * DQIX_HERO_SIZE;
        if (b[hero + DQIX_HERO_VOCATION] != 6
            || b[hero + DQIX_HERO_LEVELS + 6] != 1
            || b[hero + DQIX_HERO_LEVELS + (unsigned int)target] != 1
            || dqix_read32(b + hero + DQIX_HERO_EXPS + 6 * 4) > 7
            || dqix_read32(b + hero + DQIX_HERO_EXPS + (unsigned int)target * 4) != 0)
            return -1;
        /* Minstrel EXP may only be 0 or 7, not values 1-6. */
        uint32_t exp = dqix_read32(b + hero + DQIX_HERO_EXPS + 6 * 4);
        if (exp != 0 && exp != 7) return -1;
        vocation_offsets[slot] = base + hero + DQIX_HERO_VOCATION;
    }

    for (int slot = 0; slot < 2; ++slot) {
        unsigned char* b = image + (size_t)slot * DQIX_SLOT_SIZE;
        image[vocation_offsets[slot]] = (unsigned char)target;
        dqix_write32(b + 132, dqix_crc32(b + 136, 28644 - 136));
    }
    return 1;
}
