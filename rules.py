common_rules = {
    'config_file': [
        {'path': '/config.inc', 'status': 200, 'type_no': 'html'},
        {'path': '/config.php.bak', 'status': 200, 'type': 'application/octet-stream'},
        {'path': '/db.php.bak', 'status': 200, 'type': 'application/octet-stream'},
        {'path': '/conf/config.ini', 'status': 200, 'type_no': 'html'},
    ],
    'shell_scripts': [
        {'path': '/test.sh', 'status': 200, 'tag': '#!/'}
    ],
    'editor': [
        # Ueditor
        {'path': '/static/common/lib/ueditor/ueditor.config.js', 'status': 200, 'type': 'application/javascript'},
        {'path': '/statics/modules/ueditor/ueditor.config.js', 'status': 200, 'type': 'application/javascript'},
        {'path': '/static/js/ueditor/ueditor.config.js', 'status': 200, 'type': 'application/javascript'},
        {'path': '/ueditor/ueditor.config.js', 'status': 200, 'type': 'application/javascript'},

        # kindeditor
        {'path': '/kindeditor/kindeditor-all.js', 'status': 200, 'type': 'application/javascript'},
        {'path': '/statics/modules/kindeditor/kindeditor-all.js', 'status': 200, 'type': 'application/javascript'},
        {'path': '/static/js/kindeditor/kindeditor-all.js', 'status': 200, 'type': 'application/javascript'},
        {'path': '/static/common/lib/kindeditor/kindeditor-all.js', 'status': 200, 'type': 'application/javascript'},
    ],
    'test_page': [
        {'path': '/test.php', 'status': 200, 'type': 'html'},
        {'path': '/1.php', 'status': 200, 'type': 'html'},
        {'path': '/a.php', 'status': 200, 'type': 'html'},
        {'path': '/test1.php', 'status': 200, 'type': 'html'},
        {'path': '/test.html', 'status': 200, 'type': 'html'},
        {'path': '/test1.html', 'status': 200, 'type': 'html'},
        {'path': '/test.txt', 'status': 200, 'type': 'text/plain'},
        {'path': '/test.jsp', 'status': 200, 'type': 'html'},
    ],
    'spring': [
        {'path': '/env', 'status': 200, 'type': 'application'},
        {'path': '/trace', 'status': 200, 'type': 'application'},
        {'path': '/info', 'status': 200, 'type': 'application'},
        {'path': '/metrics', 'status': 200, 'type': 'application'},
        {'path': '/mappings', 'status': 200, 'type': 'application'},
        {'path': '/monitor', 'status': 200, 'type': 'application'},
        {'path': '/heapdump', 'status': 200, 'type': 'application/octet-stream'},
        {'path': '/dump', 'status': 200, 'type': 'application'},
        {'path': '/health', 'status': 200, 'type': 'application'},
        {'path': '/loggers', 'status': 200, 'type': 'application'},
        {'path': '/auditevents', 'status': 200, 'type': 'application'},
        {'path': '/autoconfig', 'status': 200, 'type': 'application'},
        {'path': '/beans', 'status': 200, 'type': 'application'},
        {'path': '/configprops', 'status': 200, 'type': 'application'},
        {'path': '/actuator/env', 'status': 200, 'type': 'application'},
        {'path': '/actuator/trace', 'status': 200, 'type': 'application'},
        {'path': '/actuator/info', 'status': 200, 'type': 'application'},
        {'path': '/actuator/metrics', 'status': 200, 'type': 'application'},
        {'path': '/actuator/mappings', 'status': 200, 'type': 'application'},
        {'path': '/actuator/monitor', 'status': 200, 'type': 'application'},
        {'path': '/actuator/heapdump', 'status': 200, 'type': 'application/octet-stream'},
        {'path': '/actuator/dump', 'status': 200, 'type': 'application'},
        {'path': '/actuator/health', 'status': 200, 'type': 'application'},
        {'path': '/actuator/loggers', 'status': 200, 'type': 'application'},
        {'path': '/actuator/auditevents', 'status': 200, 'type': 'application'},
        {'path': '/actuator/autoconfig', 'status': 200, 'type': 'application'},
        {'path': '/actuator/beans', 'status': 200, 'type': 'application'},
        {'path': '/actuator/configprops', 'status': 200, 'type': 'application'},
        {'path': '/swagger-ui.html', 'status': 200, 'type': 'text/html', 'tag': '<title>Swagger UI</title>'},
        {'path': '/actuator/swagger-ui.html', 'status': 200, 'type': 'text/html', 'tag': '<title>Swagger UI</title>'},
        {'path': '/v1.1/swagger-ui.html', 'status': 200, 'type': 'text/html', 'tag': '<title>Swagger UI</title>'},
        {'path': '/v1.2/swagger-ui.html', 'status': 200, 'type': 'text/html', 'tag': '<title>Swagger UI</title>'},
        {'path': '/v1.3/swagger-ui.html', 'status': 200, 'type': 'text/html', 'tag': '<title>Swagger UI</title>'},
        {'path': '/v1.4/swagger-ui.html', 'status': 200, 'type': 'text/html', 'tag': '<title>Swagger UI</title>'},
        {'path': '/v1.5/swagger-ui.html', 'status': 200, 'type': 'text/html', 'tag': '<title>Swagger UI</title>'},
        {'path': '/v1.6/swagger-ui.html', 'status': 200, 'type': 'text/html', 'tag': '<title>Swagger UI</title>'},
        {'path': '/v1.7/swagger-ui.html', 'status': 200, 'type': 'text/html', 'tag': '<title>Swagger UI</title>'},
        {'path': '/v1.8/swagger-ui.html', 'status': 200, 'type': 'text/html', 'tag': '<title>Swagger UI</title>'},
        {'path': '/v1.9/swagger-ui.html', 'status': 200, 'type': 'text/html', 'tag': '<title>Swagger UI</title>'},
        {'path': '/v2.0/swagger-ui.html', 'status': 200, 'type': 'text/html', 'tag': '<title>Swagger UI</title>'},
        {'path': '/v2.1/swagger-ui.html', 'status': 200, 'type': 'text/html', 'tag': '<title>Swagger UI</title>'},
        {'path': '/v2.2/swagger-ui.html', 'status': 200, 'type': 'text/html', 'tag': '<title>Swagger UI</title>'},
        {'path': '/v2.3/swagger-ui.html', 'status': 200, 'type': 'text/html', 'tag': '<title>Swagger UI</title>'},
    ],
    'web_app': [
        {'path': '/phpmyadmin/', 'status': 200, 'type': 'text/html', 'tag': '<title>phpMyAdmin</title>'},
        {'path': '/PhpMyAdmin/', 'status': 200, 'type': 'text/html', 'tag': '<title>phpMyAdmin</title>'},
        {'path': '/solr/', 'status': 200, 'type': 'text/html', 'tag': '<title>Solr Admin</title>'},
        {'path': '/Solr/', 'status': 200, 'type': 'text/html', 'tag': '<title>Solr Admin</title>'},
        {'path': '/console/login/LoginForm.jsp', 'status': 200, 'type': 'text/html', 'tag': 'WebLogic Server'},
        {'path': '/web-console/index.html', 'status': 200, 'type': 'text/html', 'tag': 'Jboss'},
        {'path': '/admin-console/index.html', 'status': 200, 'type': 'text/html', 'tag': 'Jboss'},
        {'path': '/axis2-admin/', 'status': 200, 'type': 'text/html', 'tag': 'axis2-web'},
        {'path': '/services/listServices', 'status': 200, 'type': 'text/html', 'tag': 'axis2-web'}
    ],
    'other': [
    ]
}

white_rules = [
]

black_rules = [
]
