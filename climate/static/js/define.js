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


var argument_manager = {
	total: 0,
	arguments: null,
	stop: false, // for accordion

	init: function(arguments) {
		this.total = arguments.children().length;
		arguments.each(function(){ argument_manager.setupArgumentRow($(this)); });
		this.arguments = arguments;
		this.arguments.find('#argument-empty').hide();
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
		var newRow = $('div#argument-empty div.row-inner').clone();
		var position = this.arguments.children().length;

		this.total += 1;
		var newRowName = 'Argument' + this.total;

		// set up default values.
		newRow.attr('id', this.total);
		newRow.find('input.p_rank').val(position);
		newRow.find('input.p_name').val(newRowName);
		newRow.find('tr.optional').hide();

		// setup dependency list based on existing arguments.
		newRow.find('select.p_depending_argument').html(function() {
			var options = '<option>None</option>';
			$('div#arguments input.p_name').each(function() {
				var name = $(this).val();
				options += '<option value="' + name + '">' + name + '</option>';
			});
			return options;
		});

		// add the new argument to other argument's dependency list.
		$('select.p_depending_argument')
			.append('<option value="' + newRowName + '">' + newRowName + '</option>');

		// add to the form.
		this.arguments.append(newRow);

		// wrap the new row into the structure required by accordion.
		newRow.wrap("<div class='row' id='row_" + this.total + "'></div>")
			  .before('<h4><a href="#" class="row-title">' + newRowName + '</a></h4>');


		// setup events.
		this.setupAccordion();
		this.arguments.accordion("option", "active", position);
		this.setupArgumentRow(newRow);

		return false;
	},

	_refreshOrder: function(){
		var order = this.arguments.sortable("toArray");
		for (var i = 0; i < order.length; i++) {
			this.arguments.children('div#' + order[i]).find('input.p_rank').val(i);
		}
	},

	setupArgumentRow:function(arg) {
		// hide rank. this is managed by accordion order.
		arg.find(".p_rank").hide();

		// auto complete for format
		arg.find('input.p_format').autocomplete({ source: formatSource});

		// hide advanced options by default
		arg.find('div.full').hide();

		// toggle advanced portion of the form
		arg.find('button.advancedToggle').click(function() {
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
		arg.find('button.deleteArg').click(function() {
			// don't do anything if there's only one argument in the form.
			if (this.total > 1) {
				var row = $(this).closest('div.row');
				var name = row.find('input.p_name').val();
				row.remove();
				$('select.p_depending_argument option[value="' + name + '"]').remove();
				this.setupAccordion();
				this._refreshOrder();
			}
			return false;
		});

	}
};

(function(){
	$(document).ready(function() {
		$('#tabs').tabs();

		$('.helptip').tooltipsy({
			alignTo: 'cursor',
			offset: [-300, 0],
			content : function() { return $('div#helptip').html(); },
			css: tooltip_css});

		argument_manager.init($('#arguments'));
		argument_manager.setupAccordion();

		$('button#addArg').click(function(){
			argument_manager.addArg();
			return false;
		});

	});
})();