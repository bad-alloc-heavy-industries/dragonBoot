# SPDX-License-Identifier: BSD-3-Clause
from logging import *
from sys import stdout
from time import strftime

__all__ = (
	'configureLogging',
)

class DragonFormatter:
	prefixes = {
		FATAL: '\x1B[31;1m[!]\x1B[0m',
		ERROR: '\x1B[31m[!]\x1B[0m',
		WARN: '\x1B[33m[~]\x1B[0m',
		INFO: '\x1B[36m[~]\x1B[0m',
		DEBUG: '\x1B[34m[~]\x1B[0m',
		NOTSET: '\x1B[35m[*]\x1B[0m',
	}

	def formatMessage(self, record : LogRecord) -> str:
		prefix = self.prefixes[record.levelno]
		if 'luna/gateware/' in record.pathname:
			prefix = f'{prefix} (LUNA)'
		return f'{prefix} {record.message}'

	def format(self, record : LogRecord) -> str:
		record.message = record.getMessage()
		message = self.formatMessage(record)
		return message

def configureLogging():
	handler = StreamHandler(stdout)
	handler.setFormatter(DragonFormatter())
	basicConfig(level = INFO, handlers = (handler,))
