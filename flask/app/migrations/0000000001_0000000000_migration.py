
from lib.base_migration import BaseMigration

revision = "0000000001"
down_revision = "0000000000"

migration = BaseMigration()


def upgrade():
    # write migration here
    migration.create_table(
        'clickwrap',
        """
            `entity_id` varchar(32) NOT NULL,
            `version` varchar(32) NOT NULL,
            `previous_version` varchar(32) DEFAULT '00000000000000000000000000000000',
            `active` tinyint(1) DEFAULT '1',
            `latest` tinyint(1) DEFAULT '1',
            `changed_by_id` varchar(32) DEFAULT NULL,
            `changed_on` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            `content` TEXT NOT NULL,
            `content_version` varchar(16) NOT NULL,
            `content_md5` varchar(32) NOT NULL,
            `status` varchar(16) DEFAULT NULL,
            PRIMARY KEY (`entity_id`,`version`),
            INDEX latest_ind (`entity_id`,`latest`,`active`)
        """
    )
    migration.create_table(
        'clickwrap_acceptance',
        """
            `entity_id` varchar(32) NOT NULL,
            `version` varchar(32) NOT NULL,
            `previous_version` varchar(32) DEFAULT '00000000000000000000000000000000',
            `active` tinyint(1) DEFAULT '1',
            `latest` tinyint(1) DEFAULT '1',
            `changed_by_id` varchar(32) DEFAULT NULL,
            `changed_on` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            `ip_address` varchar(32) NOT NULL,
            `timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
            `user_id` varchar(32) NOT NULL,
            `clickwrap_version` varchar(32) NOT NULL,
            `clickwrap_content_md5` varchar(32) NOT NULL,
            `clickwrap_content_version` varchar(16) NOT NULL,
            PRIMARY KEY (`entity_id`,`version`),
            INDEX by_user_id (`user_id`, `clickwrap_content_version`, `latest`)
        """
    )
    migration.update_version_table(version=revision)


def downgrade():
    # write migration here
    migration.drop_table('clickwrap')
    migration.drop_table('clickwrap_acceptance')
    migration.update_version_table(version=down_revision)

