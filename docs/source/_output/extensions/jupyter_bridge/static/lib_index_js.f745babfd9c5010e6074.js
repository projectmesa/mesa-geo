"use strict";
(self["webpackChunkjupyter_bridge"] = self["webpackChunkjupyter_bridge"] || []).push([["lib_index_js"],{

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   CustomOutputArea: () => (/* binding */ CustomOutputArea),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_codeeditor__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/codeeditor */ "webpack/sharing/consume/default/@jupyterlab/codeeditor");
/* harmony import */ var _jupyterlab_codeeditor__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_codeeditor__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _jupyterlab_outputarea__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @jupyterlab/outputarea */ "webpack/sharing/consume/default/@jupyterlab/outputarea");
/* harmony import */ var _jupyterlab_outputarea__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_outputarea__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _jupyterlab_rendermime__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @jupyterlab/rendermime */ "webpack/sharing/consume/default/@jupyterlab/rendermime");
/* harmony import */ var _jupyterlab_rendermime__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_rendermime__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _style_index_css__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ../style/index.css */ "./style/index.css");
/* harmony import */ var _fortawesome_fontawesome_free_css_all_min_css__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! @fortawesome/fontawesome-free/css/all.min.css */ "./node_modules/@fortawesome/fontawesome-free/css/all.min.css");
// Import necessary dependencies from React, JupyterLab, and other modules








// Define CSS classes used in the cell footer.
const CSS_CLASSES = {
    CELL_FOOTER: 'jp-CellFooter',
    CELL_FOOTER_DIV: 'ct-cellFooterContainer',
    CELL_FOOTER_BUTTON: 'ct-cellFooterBtn',
    CELL_TOGGLE_BUTTON: '.ct-toggleBtn',
    CUSTOM_OUTPUT_AREA: 'custom-output-area',
};
// Define command constants
const COMMANDS = {
    HIDE_CELL_CODE: 'hide-cell-code',
    SHOW_CELL_CODE: 'show-cell-code',
    RUN_SELECTED_CODECELL: 'run-selected-codecell',
    CLEAR_SELECTED_OUTPUT: 'clear-output-cell',
    TOGGLE_EXPL_CELL: '',
};
// Function to activate custom commands
function activateCommands(app, tracker) {
    // Output a message to the console to indicate activation
    console.log('JupyterLab extension is activated!');
    // Wait for the app to be restored before proceeding
    Promise.all([app.restored]).then(([params]) => {
        const { commands, shell } = app;
        // Function to get the current NotebookPanel
        function getCurrent(args) {
            const widget = tracker.currentWidget;
            const activate = args.activate !== false;
            if (activate && widget) {
                shell.activateById(widget.id);
            }
            return widget;
        }
        /**
        * Function to check if the command should be enabled.
        * It checks if there is a current notebook widget and if it matches the app's current widget.
        * If both conditions are met, the command is considered enabled.
        */
        function isEnabled() {
            return (tracker.currentWidget !== null &&
                tracker.currentWidget === app.shell.currentWidget);
        }
        // Define a command to toggle the visibility of the explanatory markdown cell
        commands.addCommand(COMMANDS.TOGGLE_EXPL_CELL, {
            label: 'Toggle Explanatory Cell',
            execute: () => {
                const notebookPanel = tracker.currentWidget;
                if (!notebookPanel)
                    return; // Exit if no notebook is focused
                const cells = notebookPanel.content.widgets;
                const activeCellIndex = cells.findIndex(cell => notebookPanel.content.isSelectedOrActive(cell));
                if (activeCellIndex > 0) { // Ensure there is a preceding cell
                    const precedingCell = cells[activeCellIndex - 1];
                    if (precedingCell.model.type === 'markdown') {
                        // Check if the preceding markdown cell is marked as "explanatory"
                        const isExplanatory = precedingCell.model.getMetadata('explanatory') === true;
                        if (isExplanatory) {
                            //Apply the class hidden to set the display to none
                            precedingCell.toggleClass('hidden');
                        }
                    }
                }
            },
            isEnabled
        });
        // Define a command to hide the code in the current cell
        commands.addCommand(COMMANDS.HIDE_CELL_CODE, {
            label: 'Hide Cell',
            execute: args => {
                const current = getCurrent(args);
                if (current) {
                    const { content } = current;
                    _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_2__.NotebookActions.hideCode(content);
                }
            },
            isEnabled
        });
        // Define a command to show the code in the current cell
        commands.addCommand(COMMANDS.SHOW_CELL_CODE, {
            label: 'Show Cell',
            execute: args => {
                const current = getCurrent(args);
                if (current) {
                    const { content } = current;
                    _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_2__.NotebookActions.showCode(content);
                }
            },
            isEnabled
        });
        // Define a command to run the code in the current cell
        commands.addCommand(COMMANDS.RUN_SELECTED_CODECELL, {
            label: 'Run Cell',
            execute: args => {
                const current = getCurrent(args);
                if (current) {
                    const { context, content } = current;
                    _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_2__.NotebookActions.run(content, context.sessionContext);
                }
            },
            isEnabled
        });
        commands.addCommand(COMMANDS.CLEAR_SELECTED_OUTPUT, {
            label: 'Clear Output',
            execute: args => {
                const current = getCurrent(args);
                if (current) {
                    const { content } = current;
                    _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_2__.NotebookActions.clearOutputs(content);
                }
            },
            isEnabled
        });
    });
    // Add a listener to handle when notebooks are loaded or when new cells are added to them
    tracker.widgetAdded.connect((sender, notebookPanel) => {
        var _a;
        // Add a listener for when the content of any cell in the notebook changes
        const model = notebookPanel.content.model;
        if (model === null)
            return;
        (_a = notebookPanel.content.model) === null || _a === void 0 ? void 0 : _a.cells.changed.connect((sender, change) => {
            if (change.type === 'add' || change.type === 'set') {
                change.newValues.forEach((cellModel) => {
                    if (cellModel.type === 'markdown') {
                        // Directly using cellModel to access and modify the cell's content and metadata
                        let cellText = cellModel.toJSON().source;
                        const firstLine = cellText.split('\n')[0].trim();
                        if (firstLine.includes('#explanatory')) {
                            // Mark the cell as explanatory
                            cellModel.setMetadata('explanatory', true);
                            // Remove the #explanatory marker from the cell text
                            // Not working...
                            cellText = cellText.replace('#explanatory', '').trim();
                            console.log('Remove explanatory marker and cellText value: ' + cellText);
                            cellModel.toJSON().source = cellText; // Directly update the cell's text
                        }
                        else if (firstLine.includes('#notexplanatory')) {
                            cellModel.deleteMetadata('explanatory');
                            // Remove the #notexplanatory marker from the cell text
                            // Not working...
                            cellText = cellText.replace('#notexplanatory', '').trim();
                            cellModel.toJSON().source = cellText; // Directly update the cell's text
                        }
                    }
                });
            }
        });
    });
    //Event listener to collapse code cells when a notebook is loaded
    tracker.widgetAdded.connect((sender, panel) => {
        console.log('Notebook widget added');
        function collapseAllCodeCells(panel) {
            const { content } = panel;
            content.widgets.forEach(cell => {
                if (cell.model.type === 'code') {
                    _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_2__.NotebookActions.hideAllCode(content);
                }
            });
        }
        // Function to handle initial setup to flag explanatory cells and their related code cells
        function setupCellFlags(panel) {
            let codeCellCounter = 0; //debugging counter
            //First pass: set "has_explanation' to false for all code cells
            panel.content.widgets.forEach((cell, index) => {
                // Ensure every code cell has 'has_explanation' set to false initially
                if (cell.model.type === 'code') {
                    cell.addClass('ct-code-cell');
                    cell.model.setMetadata('has_explanation', false);
                }
            });
            let previousCellIsExplanatory = false;
            // Second pass: Check each cell and update "has_explanation" based on the previous cell's "explanatory" status
            panel.content.widgets.forEach((cell, index) => {
                if (cell.model.type === 'markdown') {
                    const isExplanatory = cell.model.getMetadata('explanatory') === true;
                    if (isExplanatory) {
                        cell.addClass('ct-explanatory-cell');
                        cell.addClass('hidden');
                    }
                    previousCellIsExplanatory = isExplanatory;
                }
                else if (cell.model.type === 'code') {
                    codeCellCounter++; //Increment for each code cell encountered
                    if (previousCellIsExplanatory) {
                        console.log('Entering code cell {codeCellCounter} after an explanatory cell');
                        cell.model.setMetadata('has_explanation', true);
                        previousCellIsExplanatory = false;
                    }
                    else {
                        console.log(`Entering code cell ${codeCellCounter} with no preceding explanatory cell`);
                    }
                    previousCellIsExplanatory = false; //Reset flag
                }
                else {
                    //Reset flag for non-code, non-markdown cells if any
                    console.log('None code, non markdown');
                    previousCellIsExplanatory = false;
                }
            });
            console.log('Completed setting has_explanation flags.');
        }
        // Collapse code cells when the current notebook is loaded
        panel.context.ready.then(() => {
            console.log('Notebook context is ready');
            collapseAllCodeCells(panel);
            setupCellFlags(panel);
            // Additional debugging: Log the metadata of all cells
            console.log('Logging cell metadata after setup...');
            panel.content.widgets.forEach((cell, index) => {
                console.log(`Cell ${index} (${cell.model.type}) metadata:`, cell.model.metadata);
            });
        });
    });
    return Promise.resolve();
}
/**
 * Extend the default implementation of an `IContentFactory`.
 */
class ContentFactoryWithFooterButton extends _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_2__.NotebookPanel.ContentFactory {
    constructor(commands, options) {
        super(options); // Pass options to the superclass constructor
        this.commands = commands;
    }
    createCellFooter() {
        // Now that commands are a member of this class, you can pass them to CellFooterWithButton
        return new CellFooterWithButton(this.commands);
    }
}
// interface RunButtonProps {
//   commands: CommandRegistry;
// }
// class RunButton extends React.Component<RunButtonProps> {
//   private RUN_ICON = 'fa-solid fa-circle-play';
//   constructor(props: RunButtonProps, commands: CommandRegistry) {
//     super(props);
//     this.handleRunClick = this.handleRunClick.bind(this);
//   }
//   handleRunClick() {
//     console.log("Clicked run cell");
//     this.props.commands.execute(COMMANDS.RUN_SELECTED_CODECELL);
//   }
//   render() {
//     return React.createElement(
//       'button',
//       {
//         className: CSS_CLASSES.CELL_FOOTER_BUTTON,
//         title: 'Click to run this cell',
//         onClick: () => this.handleRunClick(),
//       },
//       React.createElement('i', { className: this.RUN_ICON })
//     );
//   }
// }
/*
 * Extend the default implementation of a cell footer with custom buttons.
 */
class CellFooterWithButton extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.ReactWidget {
    constructor(commands) {
        super();
        this.codeVisible = false;
        this.explVisible = false;
        this.RUN_ICON = 'fa-solid fa-circle-play';
        this.CLEAR_ICON = 'fa-solid fa-circle-xmark';
        this.HIDE_ICON = 'fa-solid fa-eye-slash';
        this.SHOW_ICON = 'fa-solid fa-eye';
        this.EXPL_ICON = 'fa-solid fa-book';
        this.addClass(CSS_CLASSES.CELL_FOOTER);
        this.commands = commands;
        // Add an event listener to the blue bar element
        this.node.addEventListener('click', (event) => {
            // Prevent the default behavior (collapsing/expanding)
            event.preventDefault();
        });
    }
    render() {
        const toggleIcon = this.codeVisible ? this.HIDE_ICON : this.SHOW_ICON;
        return react__WEBPACK_IMPORTED_MODULE_0__.createElement("div", { className: CSS_CLASSES.CELL_FOOTER_DIV }, react__WEBPACK_IMPORTED_MODULE_0__.createElement("button", {
            className: CSS_CLASSES.CELL_FOOTER_BUTTON,
            title: "Toggle Explanation",
            onClick: () => {
                console.log("clicked explain");
                this.explVisible = !this.explVisible;
                this.commands.execute(COMMANDS.TOGGLE_EXPL_CELL);
            },
        }, react__WEBPACK_IMPORTED_MODULE_0__.createElement("i", { className: this.EXPL_ICON })), react__WEBPACK_IMPORTED_MODULE_0__.createElement("button", {
            className: `${CSS_CLASSES.CELL_FOOTER_BUTTON} ${CSS_CLASSES.CELL_TOGGLE_BUTTON}`,
            title: "Click to hide or show code",
            onClick: () => {
                console.log("Clicked toggle cell visibility");
                this.codeVisible = !this.codeVisible;
                if (this.codeVisible) {
                    this.commands.execute(COMMANDS.SHOW_CELL_CODE);
                }
                else {
                    this.commands.execute(COMMANDS.HIDE_CELL_CODE);
                }
                this.update();
            },
        }, react__WEBPACK_IMPORTED_MODULE_0__.createElement("i", { className: toggleIcon })), react__WEBPACK_IMPORTED_MODULE_0__.createElement("button", {
            className: CSS_CLASSES.CELL_FOOTER_BUTTON,
            title: "Click to run this cell",
            onClick: () => {
                console.log("Clicked run cell");
                this.commands.execute(COMMANDS.RUN_SELECTED_CODECELL);
            },
        }, react__WEBPACK_IMPORTED_MODULE_0__.createElement("i", { className: this.RUN_ICON })), react__WEBPACK_IMPORTED_MODULE_0__.createElement("button", {
            className: CSS_CLASSES.CELL_FOOTER_BUTTON,
            title: "Click to clear cell output",
            onClick: () => {
                console.log("Clicked clear output");
                this.commands.execute(COMMANDS.CLEAR_SELECTED_OUTPUT);
            },
        }, react__WEBPACK_IMPORTED_MODULE_0__.createElement("i", { className: this.CLEAR_ICON })));
    }
}
// Define a custom output area
class CustomOutputArea extends _jupyterlab_outputarea__WEBPACK_IMPORTED_MODULE_4__.OutputArea {
    constructor(commands) {
        // Create a RenderMimeRegistry instance
        const rendermime = new _jupyterlab_rendermime__WEBPACK_IMPORTED_MODULE_5__.RenderMimeRegistry();
        super({
            rendermime,
            contentFactory: _jupyterlab_outputarea__WEBPACK_IMPORTED_MODULE_4__.OutputArea.defaultContentFactory,
            model: new _jupyterlab_outputarea__WEBPACK_IMPORTED_MODULE_4__.OutputAreaModel({ trusted: true }),
        });
        this.addClass(CSS_CLASSES.CUSTOM_OUTPUT_AREA);
    }
}
/**
 * Define a JupyterLab extension to add footer buttons to code cells.
 */
const footerButtonExtension = {
    id: 'jupyterlab-cell_toolbar',
    autoStart: true,
    activate: activateCommands,
    requires: [_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_2__.INotebookTracker]
};
/**
 * Define a JupyterLab extension to override the default notebook cell factory.
 */
const cellFactory = {
    id: 'jupyter_bridge:plugin',
    description: 'A JupyterLab extension that adds footer buttons to code cells for improved interactivity and visibility control, supporting operations like running cells, hiding/showing code, and managing output directly from the cell interface. Initial functionality included to mark documentation cells that are controlled by their corresponding code cells.',
    provides: _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_2__.NotebookPanel.IContentFactory,
    requires: [_jupyterlab_codeeditor__WEBPACK_IMPORTED_MODULE_3__.IEditorServices],
    autoStart: true,
    activate: (app, editorServices) => {
        // tslint:disable-next-line:no-console
        console.log('JupyterLab extension jupyter_bridge is activated!', 'overrides default nootbook content factory');
        const { commands } = app;
        const editorFactory = editorServices.factoryService.newInlineEditor;
        return new ContentFactoryWithFooterButton(commands, { editorFactory });
    }
};
/**
 * Export this plugins as default.
 */
const plugins = [
    footerButtonExtension,
    cellFactory
];
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugins);


/***/ }),

/***/ "./node_modules/css-loader/dist/cjs.js!./style/base.css":
/*!**************************************************************!*\
  !*** ./node_modules/css-loader/dist/cjs.js!./style/base.css ***!
  \**************************************************************/
/***/ ((module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/sourceMaps.js */ "./node_modules/css-loader/dist/runtime/sourceMaps.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/api.js */ "./node_modules/css-loader/dist/runtime/api.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__);
// Imports


var ___CSS_LOADER_EXPORT___ = _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default()((_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default()));
// Module
___CSS_LOADER_EXPORT___.push([module.id, `/*
    See the JupyterLab Developer Guide for useful CSS Patterns:

    https://jupyterlab.readthedocs.io/en/stable/developer/css.html
*/
`, "",{"version":3,"sources":["webpack://./style/base.css"],"names":[],"mappings":"AAAA;;;;CAIC","sourcesContent":["/*\r\n    See the JupyterLab Developer Guide for useful CSS Patterns:\r\n\r\n    https://jupyterlab.readthedocs.io/en/stable/developer/css.html\r\n*/\r\n"],"sourceRoot":""}]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ }),

/***/ "./node_modules/css-loader/dist/cjs.js!./style/index.css":
/*!***************************************************************!*\
  !*** ./node_modules/css-loader/dist/cjs.js!./style/index.css ***!
  \***************************************************************/
/***/ ((module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/sourceMaps.js */ "./node_modules/css-loader/dist/runtime/sourceMaps.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/api.js */ "./node_modules/css-loader/dist/runtime/api.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _node_modules_css_loader_dist_cjs_js_base_css__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! -!../node_modules/css-loader/dist/cjs.js!./base.css */ "./node_modules/css-loader/dist/cjs.js!./style/base.css");
// Imports



var ___CSS_LOADER_EXPORT___ = _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default()((_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default()));
___CSS_LOADER_EXPORT___.i(_node_modules_css_loader_dist_cjs_js_base_css__WEBPACK_IMPORTED_MODULE_2__["default"]);
// Module
___CSS_LOADER_EXPORT___.push([module.id, `.jp-Cell .ct-cellFooterContainer {
    display: flex;
    flex-direction: row; /* Ensure horizontal alignment */
    justify-content: flex-start; /* Move button to the left */
    align-items: center; /* Vertically center the button */
   }

   .jp-Cell .ct-cellFooterBtn {
     color: #fff;
     opacity: 0.7;
     font-size: 0.65rem;
     font-weight: 500;
     text-transform: uppercase;
     border: none;
     padding: 4px 8px;
     margin: 0.2rem 0;
     text-shadow: 0px 0px 5px rgba(0, 0, 0, 0.15);
     outline: none;
     cursor: pointer;
     user-select: none;
     margin-left: 0px;
     margin-right: 4px;
   }

   .jp-Placeholder-content .jp-PlaceholderText,
   .jp-Placeholder-content .jp-MoreHorizIcon {
     display: none;
   }

   /* Disable default cell collapsing behavior */
  .jp-InputCollapser,
  .jp-OutputCollapser,
  .jp-Placeholder {
   cursor: auto !important;
   pointer-events: none !important;
  }

   /* Add styles for toggle button */
   .jp-Cell .ct-toggleBtn{
     background: #f0f0f0;
   }

   .jp-Cell .ct-toggleBtn:hover{
     background-color: #ccc;
   }

   .jp-Cell .ct-toggleBtn:active{
     background-color: #999;
   }

   .ct-cellFooterBtn:active {
     background-color: var(--md-blue-600);
     text-shadow: 0px 0px 4px rgba(0, 0, 0, 0.4);
   }

   .jp-Cell .ct-cellFooterBtn:hover {
     background-color: var(--md-blue-500);
     opacity: 1;
     text-shadow: 0px 0px 7px rgba(0, 0, 0, 0.3);
     box-shadow: var(--jp-elevation-z2);
   }

   .jp-Cell .ct-cellFooterBtn {
     background: var(--md-blue-400);
   }

   .jp-CodeCell {
     display: flex !important;
     flex-direction: column;
   }

   .jp-CodeCell .jp-CellFooter {
     height: auto;
     order: 2;
   }

   .jp-Cell .jp-Cell-inputWrapper {
     margin-top: 5px;
   }

   .jp-CodeCell .jp-Cell-outputWrapper {
     order: 4;
   }

   .ct-explanatory-cell {

     width: 50%;
     float: left;
   }

   .ct-code-cell {

   }

   .hidden {
     display: none;
   }

   .lm-Widget.jp-Collapser.jp-InputCollapser.jp-Cell-inputCollapser, .lm-Widget.jp-Collapser.jp-OutputCollapser.jp-Cell-outputCollapser {
    display: none !important;
   }

   .lm-Widget.jp-InputPrompt.jp-InputArea-prompt{

   }`, "",{"version":3,"sources":["webpack://./style/index.css"],"names":[],"mappings":"AAEA;IACI,aAAa;IACb,mBAAmB,EAAE,gCAAgC;IACrD,2BAA2B,EAAE,4BAA4B;IACzD,mBAAmB,EAAE,iCAAiC;GACvD;;GAEA;KACE,WAAW;KACX,YAAY;KACZ,kBAAkB;KAClB,gBAAgB;KAChB,yBAAyB;KACzB,YAAY;KACZ,gBAAgB;KAChB,gBAAgB;KAChB,4CAA4C;KAC5C,aAAa;KACb,eAAe;KACf,iBAAiB;KACjB,gBAAgB;KAChB,iBAAiB;GACnB;;GAEA;;KAEE,aAAa;GACf;;GAEA,6CAA6C;EAC9C;;;GAGC,uBAAuB;GACvB,+BAA+B;EAChC;;GAEC,iCAAiC;GACjC;KACE,mBAAmB;GACrB;;GAEA;KACE,sBAAsB;GACxB;;GAEA;KACE,sBAAsB;GACxB;;GAEA;KACE,oCAAoC;KACpC,2CAA2C;GAC7C;;GAEA;KACE,oCAAoC;KACpC,UAAU;KACV,2CAA2C;KAC3C,kCAAkC;GACpC;;GAEA;KACE,8BAA8B;GAChC;;GAEA;KACE,wBAAwB;KACxB,sBAAsB;GACxB;;GAEA;KACE,YAAY;KACZ,QAAQ;GACV;;GAEA;KACE,eAAe;GACjB;;GAEA;KACE,QAAQ;GACV;;GAEA;;KAEE,UAAU;KACV,WAAW;GACb;;GAEA;;GAEA;;GAEA;KACE,aAAa;GACf;;GAEA;IACC,wBAAwB;GACzB;;GAEA;;GAEA","sourcesContent":["@import url('base.css');\n\n.jp-Cell .ct-cellFooterContainer {\n    display: flex;\n    flex-direction: row; /* Ensure horizontal alignment */\n    justify-content: flex-start; /* Move button to the left */\n    align-items: center; /* Vertically center the button */\n   }\n  \n   .jp-Cell .ct-cellFooterBtn {\n     color: #fff;\n     opacity: 0.7;\n     font-size: 0.65rem;\n     font-weight: 500;\n     text-transform: uppercase;\n     border: none;\n     padding: 4px 8px;\n     margin: 0.2rem 0;\n     text-shadow: 0px 0px 5px rgba(0, 0, 0, 0.15);\n     outline: none;\n     cursor: pointer;\n     user-select: none;  \n     margin-left: 0px;\n     margin-right: 4px;\n   }\n  \n   .jp-Placeholder-content .jp-PlaceholderText,\n   .jp-Placeholder-content .jp-MoreHorizIcon {\n     display: none;\n   }\n  \n   /* Disable default cell collapsing behavior */\n  .jp-InputCollapser,\n  .jp-OutputCollapser,\n  .jp-Placeholder {\n   cursor: auto !important;\n   pointer-events: none !important;\n  }\n  \n   /* Add styles for toggle button */\n   .jp-Cell .ct-toggleBtn{\n     background: #f0f0f0;\n   }\n  \n   .jp-Cell .ct-toggleBtn:hover{\n     background-color: #ccc;\n   }\n  \n   .jp-Cell .ct-toggleBtn:active{\n     background-color: #999;\n   }\n   \n   .ct-cellFooterBtn:active {\n     background-color: var(--md-blue-600);\n     text-shadow: 0px 0px 4px rgba(0, 0, 0, 0.4);\n   }\n   \n   .jp-Cell .ct-cellFooterBtn:hover {\n     background-color: var(--md-blue-500);\n     opacity: 1;\n     text-shadow: 0px 0px 7px rgba(0, 0, 0, 0.3);\n     box-shadow: var(--jp-elevation-z2);\n   }\n   \n   .jp-Cell .ct-cellFooterBtn {\n     background: var(--md-blue-400);\n   }\n   \n   .jp-CodeCell {\n     display: flex !important;\n     flex-direction: column;\n   }\n   \n   .jp-CodeCell .jp-CellFooter {\n     height: auto;\n     order: 2;\n   }\n   \n   .jp-Cell .jp-Cell-inputWrapper {\n     margin-top: 5px;\n   }\n   \n   .jp-CodeCell .jp-Cell-outputWrapper {\n     order: 4;\n   }\n   \n   .ct-explanatory-cell {\n     \n     width: 50%;\n     float: left;\n   }\n   \n   .ct-code-cell {\n    \n   }\n  \n   .hidden {\n     display: none;\n   }\n  \n   .lm-Widget.jp-Collapser.jp-InputCollapser.jp-Cell-inputCollapser, .lm-Widget.jp-Collapser.jp-OutputCollapser.jp-Cell-outputCollapser {\n    display: none !important;\n   }\n  \n   .lm-Widget.jp-InputPrompt.jp-InputArea-prompt{\n  \n   }"],"sourceRoot":""}]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ }),

/***/ "./style/index.css":
/*!*************************!*\
  !*** ./style/index.css ***!
  \*************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js */ "./node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js");
/* harmony import */ var _node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_style_loader_dist_runtime_styleDomAPI_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/styleDomAPI.js */ "./node_modules/style-loader/dist/runtime/styleDomAPI.js");
/* harmony import */ var _node_modules_style_loader_dist_runtime_styleDomAPI_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_node_modules_style_loader_dist_runtime_styleDomAPI_js__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _node_modules_style_loader_dist_runtime_insertBySelector_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/insertBySelector.js */ "./node_modules/style-loader/dist/runtime/insertBySelector.js");
/* harmony import */ var _node_modules_style_loader_dist_runtime_insertBySelector_js__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_node_modules_style_loader_dist_runtime_insertBySelector_js__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _node_modules_style_loader_dist_runtime_setAttributesWithoutAttributes_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/setAttributesWithoutAttributes.js */ "./node_modules/style-loader/dist/runtime/setAttributesWithoutAttributes.js");
/* harmony import */ var _node_modules_style_loader_dist_runtime_setAttributesWithoutAttributes_js__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_node_modules_style_loader_dist_runtime_setAttributesWithoutAttributes_js__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _node_modules_style_loader_dist_runtime_insertStyleElement_js__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/insertStyleElement.js */ "./node_modules/style-loader/dist/runtime/insertStyleElement.js");
/* harmony import */ var _node_modules_style_loader_dist_runtime_insertStyleElement_js__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_node_modules_style_loader_dist_runtime_insertStyleElement_js__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _node_modules_style_loader_dist_runtime_styleTagTransform_js__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/styleTagTransform.js */ "./node_modules/style-loader/dist/runtime/styleTagTransform.js");
/* harmony import */ var _node_modules_style_loader_dist_runtime_styleTagTransform_js__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_node_modules_style_loader_dist_runtime_styleTagTransform_js__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _node_modules_css_loader_dist_cjs_js_index_css__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! !!../node_modules/css-loader/dist/cjs.js!./index.css */ "./node_modules/css-loader/dist/cjs.js!./style/index.css");











var options = {};

options.styleTagTransform = (_node_modules_style_loader_dist_runtime_styleTagTransform_js__WEBPACK_IMPORTED_MODULE_5___default());
options.setAttributes = (_node_modules_style_loader_dist_runtime_setAttributesWithoutAttributes_js__WEBPACK_IMPORTED_MODULE_3___default());

      options.insert = _node_modules_style_loader_dist_runtime_insertBySelector_js__WEBPACK_IMPORTED_MODULE_2___default().bind(null, "head");

options.domAPI = (_node_modules_style_loader_dist_runtime_styleDomAPI_js__WEBPACK_IMPORTED_MODULE_1___default());
options.insertStyleElement = (_node_modules_style_loader_dist_runtime_insertStyleElement_js__WEBPACK_IMPORTED_MODULE_4___default());

var update = _node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0___default()(_node_modules_css_loader_dist_cjs_js_index_css__WEBPACK_IMPORTED_MODULE_6__["default"], options);




       /* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (_node_modules_css_loader_dist_cjs_js_index_css__WEBPACK_IMPORTED_MODULE_6__["default"] && _node_modules_css_loader_dist_cjs_js_index_css__WEBPACK_IMPORTED_MODULE_6__["default"].locals ? _node_modules_css_loader_dist_cjs_js_index_css__WEBPACK_IMPORTED_MODULE_6__["default"].locals : undefined);


/***/ })

}]);
//# sourceMappingURL=lib_index_js.f745babfd9c5010e6074.js.map