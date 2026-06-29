<template>
  <div class="app-shell">
    <header class="topbar">
      <h1>Scientific Workflow Studio</h1>

      <div class="actions">
        <button>Nouveau espace</button>
        <button>Ajouter script</button>
        <button>Sauvegarder</button>
        <button class="primary">Executer</button>
      </div>
    </header>

    <main class="workspace">
      <aside class="sidebar">
        <h2>Espaces de travail</h2>

        <section class="script-group">
          <h3>Detection APD</h3>
          <button class="script">acquisition.py</button>
          <button class="script">filtre.py</button>
          <button class="script">fft.py</button>
          <button class="script">cnn.py</button>
        </section>

        <section class="script-group">
          <h3>FPGA JESD204B</h3>
          <button class="script">capture.py</button>
          <button class="script">analyse.py</button>
        </section>
      </aside>

      <section class="main-panel">
        <nav class="tabs">
          <button class="active">Diagramme</button>
          <button>Signaux</button>
          <button>Logs</button>
          <button>Parametres</button>
        </nav>

        <section class="diagram">
          <div class="node node-a">
            <strong>acquisition.py</strong>
            <span>Sortie : signal</span>
          </div>

          <div class="connection connection-1"></div>

          <div class="node node-b">
            <strong>fft.py</strong>
            <span>Entree : signal</span>
            <span>Sortie : spectre</span>
          </div>

          <div class="connection connection-2"></div>

          <div class="node node-c">
            <strong>cnn.py</strong>
            <span>Entree : spectre</span>
            <span>Sortie : classes</span>
          </div>
        </section>
      </section>
    </main>
  </div>
</template>