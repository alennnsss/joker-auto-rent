<script setup lang="ts">
import { useI18n } from 'vue-i18n'

import { REVIEWS_URL, rating, reviews } from '@/config/reviews'
import { formatDate } from '@/utils/format'

const { t } = useI18n()
</script>

<template>
  <section class="reviews" aria-labelledby="reviews-title">
    <div class="reviews__head">
      <div>
        <i18n-t id="reviews-title" keypath="reviews.title" tag="h2" scope="global">
          <template #accent>
            <span class="text-gold">{{ t('reviews.titleAccent') }}</span>
          </template>
        </i18n-t>
        <p class="muted">{{ t('reviews.subtitle') }}</p>
      </div>
      <a :href="REVIEWS_URL" class="rating" target="_blank" rel="noopener">
        <span class="rating__value">{{ rating.value.toFixed(1).replace('.', ',') }}</span>
        <span class="rating__meta">
          <span class="rating__stars" aria-hidden="true">★★★★★</span>
          <span class="muted">{{ t('reviews.count', rating.count) }}</span>
        </span>
      </a>
    </div>

    <ul class="reviews__grid">
      <li v-for="r in reviews" :key="r.author + r.date" class="review">
        <div class="review__head">
          <span class="review__avatar" aria-hidden="true">{{ r.author.charAt(0).toUpperCase() }}</span>
          <div>
            <p class="review__author">{{ r.author }}</p>
            <p class="review__date muted">{{ formatDate(r.date) }}</p>
          </div>
        </div>
        <blockquote class="review__text">{{ r.text }}</blockquote>
      </li>
    </ul>

    <div class="reviews__more">
      <a :href="REVIEWS_URL" class="btn btn--outline" target="_blank" rel="noopener">
        {{ t('reviews.all') }}
      </a>
    </div>
  </section>
</template>

<style scoped lang="scss">
.reviews {
  &__head {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-end;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 24px;

    h2 {
      margin-bottom: 4px;
    }

    p {
      margin: 0;
    }
  }

  &__grid {
    display: grid;
    gap: 16px;
    padding: 0;
    margin: 0;
    list-style: none;

    @include media(md) {
      grid-template-columns: 1fr 1fr;
    }

    @include media(lg) {
      grid-template-columns: repeat(3, 1fr);
    }
  }

  &__more {
    display: flex;
    justify-content: center;
    margin-top: 24px;
  }
}

.rating {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 18px;
  border: 1px solid var(--color-gold-dark);
  border-radius: var(--radius);
  color: var(--color-text);

  @include hover {
    background: var(--color-gold-alpha);
  }

  &__value {
    font-size: 2rem;
    font-weight: 800;
    color: var(--color-gold);
    line-height: 1;
  }

  &__meta {
    display: flex;
    flex-direction: column;
    font-size: 0.85rem;
  }

  &__stars {
    color: var(--color-gold);
    letter-spacing: 2px;
  }
}

.review {
  @include card;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 24px;

  &__head {
    display: flex;
    align-items: center;
    gap: 12px;

    p {
      margin: 0;
    }
  }

  &__avatar {
    display: grid;
    place-items: center;
    flex: 0 0 44px;
    height: 44px;
    border-radius: 50%;
    background: var(--gradient-gold);
    color: var(--color-on-gold);
    font-weight: 700;
  }

  &__author {
    font-weight: 600;
  }

  &__date {
    font-size: 0.85rem;
  }

  &__text {
    margin: 0;
    color: var(--color-text-muted);
    line-height: 1.6;
  }
}
</style>
