/**
 * Organization: Leiden University Medical Center (LUMC)
 * Author: ztatum
 * Email: z.tatum@lumc.nl
 * Date: 10/10/12 4:20 PM
 */

// for tooltip style
var tooltip_css = {
	'padding': '10px',
	'max-width': '300px',
	'color': '#303030',
	'background-color': 'white',
	'border': '1px solid #deca7e',
	'-moz-box-shadow': '0 0 10px rgba(0, 0, 0, .5)',
	'-webkit-box-shadow': '0 0 10px rgba(0, 0, 0, .5)',
	'box-shadow': '0 0 10px rgba(0, 0, 0, .5)',
	'text-shadow': 'none'
};

// copied from galaxy.
var formatSource = [
	"Roadmaps", "Sequences", "ab1", "acedb", "afg","asn1","axt","bam","bed", "bedgraph", "bgzip", "bigbed", "bigwig",
	"blastxml", "btwisted", "cai", "charge", "checktrans", "chips", "clustal", "codata", "codcmp", "coderet", "compseq",
	"coverage", "cpgplot", "cpgreport", "csfasta", "csv", "cusp", "customtrack", "cut", "dan", "data", "dbmotif",
	"diffseq","digest", "dreg", "einverted", "eland", "elandmulti", "embl", "epestfind", "equicktandem", "est2genome",
	"etandem", "excel", "fasta", "fastq", "fastqcssanger", "fastqillumina", "fastqsanger", "fastqsolexa", "feattable",
	"fitch", "freak", "fuzznuc", "fuzzpro", "fuzztran", "garnier", "gatk_dbsnp", "gatk_interval", "gcg", "geecee",
	"genbank", "genetrack", "gff", "gff3", "gg", "gif", "gmaj.zip", "gtf", "helixturnhelix", "hennig86", "hmoment",
	"html", "ig", "interval", "interval_index", "isochore", "jackknifer", "jackknifernon", "jpg", "laj", "lav", "len",
	"maf", "mafcustomtrack",  "markx0", "markx1", "markx10", "markx2", "markx3", "match", "mega",
	"meganon", "memexml", "motif", "msf", "nametable", "ncbi", "needle", "newcpgreport", "newcpgseek",
	"nexus", "nexusnon", "noreturn", "pair", "palindrome", "pdf", "pepcoil", "pepinfo", "pepstats", "pheno",
	"phylip", "phylipnon", "picard_interval_list", "pileup", "pir", "png", "polydot", "preg", "prettyseq",
	"primersearch", "qual", "qual454",  "qualillumina", "qualsolexa",  "qualsolid", "regions", "sam", "scf",
	"score", "selex", "seqtable", "sff", "showfeat", "showorf", "simple", "sixpack", "srs", "srspair", "staden",
	"strider", "summary_tree", "supermatcher", "svg", "swiss", "syco", "tabix", "table", "tabular", "tagseq",
	"taxonomy", "textsearch", "twobit", "txt",  "vcf", "vectorstrip", "wig", "wobble", "wordcount", "wsf", "xls"];


var io_prefixes = {
	'input' : '',
	'output' : '',
	'stdin' : '<',
	'stdout' : '>',
	'stderr' : '2>'
};

var argument_manager = {
	total: 0,
	arguments: null,
	stop: false, // for accordion

	init: function(arguments) {
		this.arguments = arguments;
		this.total = arguments.children().length;
		arguments.each(function(){ arg_row_manager.setup($(this)); });
		this.setupAccordion();
	},

	setupAccordion: function (){
		this.arguments.accordion("destroy")
			.accordion({header: "> div > h4", collapsible: true, autoHeight: false})
			.sortable({axis: "y", handle: "h4", stop: function() {
					this.stop = true;
					this._refreshOrder();
					// nasty workaround from ie8
					$('body').css("display", "none").css("display", "block");
				}});

		$(".row-header").click(function(event) {
			if (this.stop) {
				event.stopImmediatePropagation();
				event.preventDefault();
				this.stop = false;
			}
		});
	},

	addArg: function(){

		this.total += 1;
		var position = this.arguments.children().length;

		var newRow = arg_row_manager.newRow(this.total, position);
		newRow.show();

		// add to the form.
		this.arguments.append(newRow);

		// setup events.
		this.setupAccordion();
		this.arguments.accordion("option", "active", position);

		return false;
	},

	_refreshOrder: function(){
		var order = this.arguments.sortable("toArray");
		for (var i = 0; i < order.length; i++) {
			this.arguments.children('div#' + order[i]).find('input.p_rank').val(i);
		}
	}
};

var arg_row_manager = {

	// for renaming an argument.
	current_name: '',

	newRow : function(row_id, position){

		var name = 'Argument' + row_id;
		var newRow = $('div#argument-empty').clone();

		newRow.attr('id', 'row_' + row_id);
		newRow.removeClass('argument-empty').addClass('row');
		newRow.find('h4 a').html(name);

		var newRowInner = newRow.find('div.row-inner');

		// set up default values.
		newRowInner.attr('id', row_id);
		newRowInner.find('input.p_rank').val(position);
		newRowInner.find('input.p_name').val(name);

		// setup dependency list based on existing arguments.
		newRowInner.find('select.p_depending_argument').html(function() {
			var options = '<option>None</option>';
			$('div#arguments input.p_name').each(function() {
				var name = $(this).val();
				options += '<option value="' + name + '">' + name + '</option>';
			});
			return options;
		});

		// add the new argument to other argument's dependency list.
		$('select.p_depending_argument')
			.append('<option value="' + name + '">' + name + '</option>');

		this.setup(newRow);

		return newRow;
	},

	setup: function(arg_row){

		// hide rank. this is managed by accordion order.
		arg_row.find("p.p_rank").hide();

		// auto complete for format
		arg_row.find('input.p_format').autocomplete({ source: formatSource});

		// hide advanced options by default
		arg_row.find('div.full').hide();

		// toggle advanced portion of the form
		arg_row.find('button.advancedToggle').click(function() {
			if ($(this).hasClass('less')) {
				$(this).removeClass('less');
				$(this).find('span').text('Show advanced options');
			} else {
				$(this).addClass('less');
				$(this).find('span').text('Hide advanced options');
			}

			$(this).closest('div.row-inner').find('div.full').toggle('hide');

			return false;
		});

		// delete an argument
		arg_row.find('button.deleteArg').click(function() {
			// don't do anything if there's only one argument in the form.
			if (argument_manager.total > 1) {
				var row = $(this).closest('div.row');
				var name = row.find('input.p_name').val();
				row.remove();
				$('select.p_depending_argument option[value="' + name + '"]').remove();
				argument_manager.setupAccordion();
				argument_manager._refreshOrder();
			}
			return false;
		});

		var arg_type = arg_row.find('select.p_arg_type');
		// hide format input from user if the arg type is not input/output.
		if (io_prefixes[arg_type.val()] === undefined) {
			arg_row.find('p.p_format').hide();
		}

		// handle changes to the argument type.
		arg_type.change(function(){
			var format = arg_row.find('p.p_format');
			var prefix = arg_row.find('input.p_prefix');
			var new_prefix = io_prefixes[$(this).val()];
			if (new_prefix === undefined){
				format.hide();
				prefix.val('');
			} else {
				format.show();
				prefix.val(new_prefix);
			}
		});

		// renaming an argument.
		arg_row.find('input.p_name')
			.focusin(function() {
				arg_row_manager.current_name = $(this).val();
			})
			.focusout(function() {
				var row = $(this).closest('div.row');
				var newName = $(this).val();
				row.find('a.row-title').html(newName);
				$('select.p_depending_parameter option[value="' + arg_row_manager.current_name + '"]')
					.attr('value', newName)
					.html(newName);
				arg_row_manager.current_name = "";
			});
	}
};

(function(){
	$(document).ready(function() {
		// use tab view to divide the form into three parts.
		$('#tabs').tabs();

		// helptip for the tool help text area.
		$('.helptip').tooltipsy({
			alignTo: 'cursor',
			offset: [-300, 0],
			content : function() { return $('div#helptip').html(); },
			css: tooltip_css});

		// hide empty argument row.
		$('#argument-empty').hide();

		// initialize arguments.
		argument_manager.init($('#arguments'));

		// new argument button.
		$('button#addArg').click(function(){
			argument_manager.addArg();
			return false;
		});

	});
})();