/* Unit tests use synthetic saves only — no game binary, ROM or save. */
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../native/dqix_vocation.c"

static void make_save(unsigned char* image, unsigned int exp) {
    memset(image, 0, DQIX_SAVE_SIZE);
    for (int slot = 0; slot < 2; ++slot) {
        unsigned char* b = image + slot * DQIX_SLOT_SIZE;
        memcpy(b, "DRAGON QUEST IX", 15);
        b[DQIX_PRESENT] = 1;
        b[DQIX_STANDBY] = 3;
        b[DQIX_PARTY] = 1;
        size_t hero = DQIX_HERO_BASE + 3 * DQIX_HERO_SIZE;
        b[hero + DQIX_HERO_VOCATION] = 6;
        for (int v = 1; v <= 6; ++v) b[hero + DQIX_HERO_LEVELS + v] = 1;
        dqix_write32(b + hero + DQIX_HERO_EXPS + 6 * 4, exp);
        dqix_write32(b + 16, dqix_crc32(b + 20, 16));
        dqix_write32(b + 36, dqix_crc32(b + 40, 92));
        dqix_write32(b + 132, dqix_crc32(b + 136, 28644 - 136));
    }
}
static void test_each_vocation(void) {
    static const char* names[] = {"warrior", "priest", "mage", "martial-artist", "thief"};
    unsigned char* image = malloc(DQIX_SAVE_SIZE);
    unsigned char* original = malloc(DQIX_SAVE_SIZE);
    assert(image && original);
    for (int exp = 0; exp <= 7; exp += 7) {
        for (int v = 0; v < 5; ++v) {
            make_save(image, (unsigned int)exp);
            memcpy(original, image, DQIX_SAVE_SIZE);
            assert(dqix_apply_start_vocation(image, DQIX_SAVE_SIZE, names[v]) == 1);
            for (int slot = 0; slot < 2; ++slot) {
                size_t base = (size_t)slot * DQIX_SLOT_SIZE;
                size_t location = base + DQIX_HERO_BASE + 3 * DQIX_HERO_SIZE
                    + DQIX_HERO_VOCATION;
                assert(image[location] == v + 1);
                /* DQIX IDs: warrior 1 priest 2 mage 3 martial 4 thief 5 */
                assert(dqix_checks_ok(image + base));
                for (size_t i = base; i < base + DQIX_SLOT_SIZE; ++i) {
                    if (image[i] != original[i]) {
                        assert(i == location || (i >= base + 132 && i < base + 136));
                    }
                }
            }
        }
    }
    free(original);
    free(image);
}
static void test_rejected_without_mutation(void) {
    unsigned char* image = malloc(DQIX_SAVE_SIZE);
    unsigned char* original = malloc(DQIX_SAVE_SIZE);
    assert(image && original);
    make_save(image, 7);
    memcpy(original, image, DQIX_SAVE_SIZE);
    assert(dqix_apply_start_vocation(image, DQIX_SAVE_SIZE, NULL) == 0);
    assert(dqix_apply_start_vocation(image, DQIX_SAVE_SIZE, "paladin") == -1);
    assert(dqix_apply_start_vocation(image, DQIX_SAVE_SIZE - 1, "mage") == -1);
    assert(memcmp(image, original, DQIX_SAVE_SIZE) == 0);

    image[DQIX_SLOT_SIZE + DQIX_HERO_BASE + 3 * DQIX_HERO_SIZE
          + DQIX_HERO_LEVELS + 6] = 2;
    memcpy(original, image, DQIX_SAVE_SIZE);
    assert(dqix_apply_start_vocation(image, DQIX_SAVE_SIZE, "mage") == -1);
    assert(memcmp(image, original, DQIX_SAVE_SIZE) == 0);

    make_save(image, 7);
    image[DQIX_SLOT_SIZE + DQIX_PRESENT] = 0;
    memcpy(original, image, DQIX_SAVE_SIZE);
    assert(dqix_apply_start_vocation(image, DQIX_SAVE_SIZE, "mage") == -1);
    assert(memcmp(image, original, DQIX_SAVE_SIZE) == 0);

    make_save(image, 7);
    image[210] ^= 1; /* corrupted first slot CRC */
    memcpy(original, image, DQIX_SAVE_SIZE);
    assert(dqix_apply_start_vocation(image, DQIX_SAVE_SIZE, "mage") == -1);
    assert(memcmp(image, original, DQIX_SAVE_SIZE) == 0);
    free(original);
    free(image);
}
int main(void) {
    test_each_vocation();
    test_rejected_without_mutation();
    puts("native starting-vocation synthetic-save tests passed");
    return 0;
}
