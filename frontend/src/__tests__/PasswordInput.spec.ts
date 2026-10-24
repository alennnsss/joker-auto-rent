import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import PasswordInput from '@/components/PasswordInput.vue'

describe('PasswordInput', () => {
  it('toggles password visibility', async () => {
    const wrapper = mount(PasswordInput, {
      props: { id: 'pwd', autocomplete: 'current-password', modelValue: 'secret123' },
    })
    const input = wrapper.get('input')
    const toggle = wrapper.get('button')

    expect(input.attributes('type')).toBe('password')
    expect(toggle.attributes('aria-label')).toBe('Показать пароль')

    await toggle.trigger('click')
    expect(input.attributes('type')).toBe('text')
    expect(toggle.attributes('aria-pressed')).toBe('true')
    expect(toggle.attributes('aria-label')).toBe('Скрыть пароль')
  })

  it('emits model updates', async () => {
    const wrapper = mount(PasswordInput, {
      props: { id: 'pwd', autocomplete: 'new-password', modelValue: '' },
    })
    await wrapper.get('input').setValue('newpass')
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual(['newpass'])
  })
})
