<script setup>
defineProps({
  tabs: Array,
  nodes: Array,
  connections: Array,
})
</script>

<template>
  <section class="main-panel">
    <nav class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab"
        :class="{ active: tab === 'Diagramme' }"
      >
        {{ tab }}
      </button>
    </nav>

    <section class="diagram">
      <div
        v-for="connection in connections"
        :key="connection.id"
        class="connection"
        :style="{
          left: `${connection.x}px`,
          top: `${connection.y}px`,
          width: `${connection.width}px`,
        }"
      ></div>

      <div
        v-for="node in nodes"
        :key="node.id"
        class="node"
        :style="{
          left: `${node.x}px`,
          top: `${node.y}px`,
        }"
      >
        <strong>{{ node.file }}</strong>

        <span
          v-for="line in node.lines"
          :key="line"
        >
          {{ line }}
        </span>
      </div>
    </section>
  </section>
</template>