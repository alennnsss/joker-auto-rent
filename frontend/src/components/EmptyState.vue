<script setup lang="ts">
defineProps<{ title: string; text?: string }>()
</script>

<template>
  <div class="empty">
    <h3 class="empty__title">{{ title }}</h3>
    <p v-if="text" class="muted">{{ text }}</p>
    <div class="empty__actions"><slot /></div>
  </div>
</template>

<style scoped lang="scss">
.empty {
  @include card;
  padding: 40px 20px;
  text-align: center;

  &__title {
    margin-bottom: 8px;
  }

  &__actions {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 12px;
    margin-top: 16px;
  }
}
</style>
