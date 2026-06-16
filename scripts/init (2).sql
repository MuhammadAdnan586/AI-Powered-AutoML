-- AutoML SaaS – Database Initialization
-- Seeds default roles and permissions on first run.

INSERT IGNORE INTO roles (name, description) VALUES
  ('admin',   'Full platform access – manage users, models, schedules'),
  ('analyst', 'Can train models, view results, generate reports'),
  ('viewer',  'Read-only access to dashboards and results');

-- Default permissions for analyst
INSERT IGNORE INTO permissions (role_id, resource, action)
SELECT r.id, p.resource, p.action
FROM roles r
CROSS JOIN (
  SELECT 'datasets' AS resource, 'read'   AS action UNION ALL
  SELECT 'datasets',             'write'             UNION ALL
  SELECT 'models',               'read'              UNION ALL
  SELECT 'models',               'write'             UNION ALL
  SELECT 'reports',              'read'              UNION ALL
  SELECT 'reports',              'write'
) p
WHERE r.name = 'analyst';

-- Default permissions for viewer
INSERT IGNORE INTO permissions (role_id, resource, action)
SELECT r.id, p.resource, p.action
FROM roles r
CROSS JOIN (
  SELECT 'datasets' AS resource, 'read' AS action UNION ALL
  SELECT 'models',               'read'           UNION ALL
  SELECT 'reports',              'read'
) p
WHERE r.name = 'viewer';
