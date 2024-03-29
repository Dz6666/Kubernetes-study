local k = import 'ksonnet/ksonnet.beta.4/k.libsonnet';

{
  _config+:: {
    namespace: 'default',

    versions+:: {
      alertmanager: 'v0.20.0',
    },

    imageRepos+:: {
      alertmanager: 'quay.io/prometheus/alertmanager',
    },

    alertmanager+:: {
      name: 'main',
      config: {
        global: {
          resolve_timeout: '5m',
        },
        inhibit_rules: [{
          source_match: {
            severity: 'critical',
          },
          target_match_re: {
            severity: 'warning|info',
          },
          equal: ['namespace', 'alertname'],
        }, {
          source_match: {
            severity: 'warning',
          },
          target_match_re: {
            severity: 'info',
          },
          equal: ['namespace', 'alertname'],
        }],
        route: {
          group_by: ['namespace'],
          group_wait: '30s',
          group_interval: '5m',
          repeat_interval: '12h',
          receiver: 'Default',
          routes: [
            {
              receiver: 'Watchdog',
              match: {
                alertname: 'Watchdog',
              },
            },
            {
              receiver: 'Critical',
              match: {
                severity: 'critical',
              },
            },
          ],
        },
        receivers: [
          {
            name: 'Default',
          },
          {
            name: 'Watchdog',
          },
          {
            name: 'Critical',
          },
        ],
      },
      replicas: 3,
    },
  },

  alertmanager+:: {
    secret:
      local secret = k.core.v1.secret;

      if std.type($._config.alertmanager.config) == 'object' then
        secret.new('alertmanager-' + $._config.alertmanager.name, {})
        .withStringData({ 'alertmanager.yaml': std.manifestYamlDoc($._config.alertmanager.config) }) +
        secret.mixin.metadata.withNamespace($._config.namespace)
      else
        secret.new('alertmanager-' + $._config.alertmanager.name, { 'alertmanager.yaml': std.base64($._config.alertmanager.config) }) +
        secret.mixin.metadata.withNamespace($._config.namespace),

    serviceAccount:
      local serviceAccount = k.core.v1.serviceAccount;

      serviceAccount.new('alertmanager-' + $._config.alertmanager.name) +
      serviceAccount.mixin.metadata.withNamespace($._config.namespace),

    service:
      local service = k.core.v1.service;
      local servicePort = k.core.v1.service.mixin.spec.portsType;

      local alertmanagerPort = servicePort.newNamed('web', 9093, 'web');

      service.new('alertmanager-' + $._config.alertmanager.name, { app: 'alertmanager', alertmanager: $._config.alertmanager.name }, alertmanagerPort) +
      service.mixin.spec.withSessionAffinity('ClientIP') +
      service.mixin.metadata.withNamespace($._config.namespace) +
      service.mixin.metadata.withLabels({ alertmanager: $._config.alertmanager.name }),

    serviceMonitor:
      {
        apiVersion: 'monitoring.coreos.com/v1',
        kind: 'ServiceMonitor',
        metadata: {
          name: 'alertmanager',
          namespace: $._config.namespace,
          labels: {
            'k8s-app': 'alertmanager',
          },
        },
        spec: {
          selector: {
            matchLabels: {
              alertmanager: $._config.alertmanager.name,
            },
          },
          endpoints: [
            {
              port: 'web',
              interval: '30s',
            },
          ],
        },
      },

    alertmanager:
      {
        apiVersion: 'monitoring.coreos.com/v1',
        kind: 'Alertmanager',
        metadata: {
          name: $._config.alertmanager.name,
          namespace: $._config.namespace,
          labels: {
            alertmanager: $._config.alertmanager.name,
          },
        },
        spec: {
          replicas: $._config.alertmanager.replicas,
          version: $._config.versions.alertmanager,
          image: $._config.imageRepos.alertmanager + ':' + $._config.versions.alertmanager,
          nodeSelector: { 'kubernetes.io/os': 'linux' },
          serviceAccountName: 'alertmanager-' + $._config.alertmanager.name,
          securityContext: {
            runAsUser: 1000,
            runAsNonRoot: true,
            fsGroup: 2000,
          },
        },
      },
  },
}
