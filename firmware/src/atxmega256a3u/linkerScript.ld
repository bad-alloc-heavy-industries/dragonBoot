/* SPDX-License-Identifier: BSD-3-Clause */
OUTPUT_FORMAT("elf32-avr")
OUTPUT_ARCH(avr:106)

MEMORY
{
	text	(rx)	: ORIGIN = 0x040000, LENGTH = 0x002000
	data	(rw!x)	: ORIGIN = 0x802000, LENGTH = 0x004000
	eeprom	(rw!x)	: ORIGIN = 0x801000, LENGTH = 0x001000
	fuse	(rw!x)	: ORIGIN = 0x820000, LENGTH = 0x000006
	lock	(rw!x)	: ORIGIN = 0x830000, LENGTH = 0x000001
	prodsig	(r!x)	: ORIGIN = 0x840000, LENGTH = 0x000100
	usersig	(rw!x)	: ORIGIN = 0x850000, LENGTH = 0x000100
}

SECTIONS
{
	/* R/O general sections (automerged into .text) */
	.hash : { *(.hash) }
	.dynsym : { *(.dynsym) }
	.dynstr : { *(.dynstr) }
	.gnu.version : { *(.gnu.version) }
	.gnu.version_d : { *(.gnu.version_d) }
	.gnu.version_r : { *(.gnu.version_r) }
	.rel.init : { *(.rel.init) }
	.rela.init : { *(.rela.init) }
	.rel.text :
		{ *(.rel.text .rel.text.* .rel.gnu.linkonce.t*) }
	.rela.text :
		{ *(.rela.text .rela.text.* .rela.gnu.linkonce.t*) }
	.rel.fini : { *(.rel.fini) }
	.rela.fini : { *(.rela.fini) }
	.rel.rodata :
		{ *(.rel.rodata .rel.rodata.* .rel.gnu.linkonce.r*) }
	.rela.rodata :
		{ *(.rela.rodata .rela.rodata.* .rela.gnu.linkonce.r*) }
	.rel.data :
		{ *(.rel.data .rel.data.* .rel.gnu.linkonce.d*) }
	.rela.data :
		{ *(.rela.data .rela.data.* .rela.gnu.linkonce.d*) }
	.rel.ctors : { *(.rel.ctors) }
	.rela.ctors : { *(.rela.ctors) }
	.rel.dtors : { *(.rel.dtors) }
	.rela.dtors : { *(.rela.dtors) }
	.rel.got : { *(.rel.got) }
	.rela.got : { *(.rela.got) }
	.rel.bss : { *(.rel.bss) }
	.rela.bss : { *(.rela.bss) }
	.rel.plt : { *(.rel.plt) }
	.rela.plt : { *(.rela.plt) }

	.text : ALIGN(2)
	{
		PROVIDE(beginText = .);
		PROVIDE(vectorAddr = .);
		*(.vectors)
		KEEP(*(.vectors))

		PROVIDE(beginTrampolines = .);
		/* Handling for jump trampolines */
		*(.trampolines)
		*(.trampolines.*)
		PROVIDE(endTrampolines = .);

		*(.progmem.*)
		*(.lowtext .lowtext.*)

		PROVIDE(beginCtors = .);
		KEEP(*(.init_array .ctors.* .ctors))
		PROVIDE(endCtors = .);

		*(.startup)
		KEEP(*(.startup))
		*(.text .text.* .gnu.linkonce.t*)
		*(.rodata.* .rodata .gnu.linkonce.r*)
		*(.hightext .hightext.* .progmemx.*)
		*(.jumptables .jumptables.*)
		PROVIDE(endText = .);
	} >text

	.stack :
	{
		/* provide 2048 bytes of stack. */
		. += 0x000800;
		PROVIDE(stackTop = . - 1);
	} >data

	.data : ALIGN(2)
	{
		PROVIDE(beginData = .);
		*(.data .data.* .gnu.linkonce.d*)
		PROVIDE(endData = .);
	} >data AT >text

	PROVIDE(addrData = LOADADDR(.data));

	.bss :
	{
		PROVIDE(beginBSS = .);
		*(.bss .bss.* COMMON)
		PROVIDE(endBSS = .);
	} >data

	.noinit :
	{
		*(.noinit .noinit.*)
	} >data

	.eeprom :
	{
		KEEP(*(.eeprom*))
	} >eeprom

	.fuse :
	{
		KEEP(*(.fuse .lfuse .hfuse .efuse))
	} >fuse

	.lock :
	{
		KEEP(*(.lock*))
	} >lock

	.prodsig :
	{
		KEEP(*(.signature*))
	} >prodsig

	/* Stabs debugging sections */
	.stab 0 : { *(.stab) }
	.stabstr 0 : { *(.stabstr) }
	.stab.excl 0 : { *(.stab.excl) }
	.stab.exclstr 0 : { *(.stab.exclstr) }
	.stab.index 0 : { *(.stab.index) }
	.stab.indexstr 0 : { *(.stab.indexstr) }
	.comment 0 : { *(.comment) }
	.note.gnu.build-id : { *(.note.gnu.build-id) }

	/* DWARF debugging sections */
	/* DWARF 1 */
	.debug 0 : { *(.debug) }
	.line 0 : { *(.line) }
	/* GNU DWARF 1 extensions */
	.debug_srcinfo 0 : { *(.debug_srcinfo) }
	.debug_sfnames 0 : { *(.debug_sfnames) }
	/* DWARF 1.1 and DWARF 2 */
	.debug_aranges 0 : { *(.debug_aranges) }
	.debug_pubnames 0 : { *(.debug_pubnames) }
	/* DWARF 2 */
	.debug_info 0 : { *(.debug_info .gnu.linkonce.wi.*) }
	.debug_abbrev 0 : { *(.debug_abbrev) }
	.debug_line 0 : { *(.debug_line .debug_line.* .debug_line_end) }
	.debug_frame 0 : { *(.debug_frame) }
	.debug_str 0 : { *(.debug_str) }
	.debug_loc 0 : { *(.debug_loc) }
	.debug_macinfo 0 : { *(.debug_macinfo) }
	/* SGI/MIPS DWARF 2 extensions */
	.debug_weaknames 0 : { *(.debug_weaknames) }
	.debug_funcnames 0 : { *(.debug_funcnames) }
	.debug_typenames 0 : { *(.debug_typenames) }
	.debug_varnames 0 : { *(.debug_varnames) }
	/* DWARF 3 */
	.debug_pubtypes 0 : { *(.debug_pubtypes) }
	.debug_ranges 0 : { *(.debug_ranges) }
	/* DWARF Extension.  */
	.debug_macro 0 : { *(.debug_macro) }
	.debug_addr 0 : { *(.debug_addr) }
	.gnu.attributes 0 : { KEEP (*(.gnu.attributes)) }
}
