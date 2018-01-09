//below line tells eslint not to mark require as wrong thinkink it runs in browser
/*eslint-env node */
var gulp = require('gulp');
var sass = require('gulp-sass');
var autoprefixer = require('gulp-autoprefixer');
var eslint = require('gulp-eslint');
var browserSync = require('browser-sync').create();
// var jasmine = require('gulp-jasmine-phantom');

//order plugin is used to order the files to be concatenated
var order = require('gulp-order');
//concat plugin is used to concat all JavaScript files into one 
var concat = require('gulp-concat');
//uglify plugin is used for minification
var uglify = require('gulp-uglify');

// gulp.task('tests', function() {
// 	return gulp.src('spec/test.js')
// 		.pipe(jasmine({
// 			integration: true,
// 			vendor: 'js/**/*.js'
// 		}));
// });

gulp.task('default',['copy-html','scripts','scripts-dist','styles','lint'], function(){
	// Below code wathes for any change in .scss file 
	// and executes the styles task whenever sass files change
	gulp.watch('./sass/**/*.scss',['styles']);
	gulp.watch('./src/js/**/*.js',['lint']);
	gulp.watch('./src/index.html',['copy-html']);
	gulp.watch('./dist/index.html').on('change',browserSync.reload);
	browserSync.init({server: './dist'});
});

gulp.task('dist',['copy-html','styles','lint','scripts-dist']);

gulp.task('scripts',function(){
	gulp.src('src/js/**/*.js')
		.pipe(concat('all.js'))
		.pipe(gulp.dest('dist/js'));
});

gulp.task('scripts-dist',function(){
	gulp.src('src/js/**/*.js')
		.pipe(order([
			'src/js/lib/jQuery.js',
			'src/js/lib/knockout-3.2.0.js',
			'src/js/app.js'
		],{ base: './' }))	
		.pipe(concat('all.js'))
		.pipe(uglify())
		.pipe(gulp.dest('dist/js'));
});

gulp.task('copy-html',function(){
	gulp.src('./src/index.html')
		.pipe(gulp.dest('./dist'));
});

gulp.task('lint', function() {
	// ESLint ignores files with "node_modules" paths. 
	// So, it's best to have gulp ignore the directory as well. 
	// Also, Be sure to return the stream from the task; 
	// Otherwise, the task may end before the stream has finished. 
	return gulp.src(['src/**/*.js','!node_modules/**','!src/js/lib/**'])
		// eslint() attaches the lint output to the "eslint" property 
		// of the file object so it can be used by other modules. 
		.pipe(eslint())
		// eslint.format() outputs the lint results to the console. 
		// Alternatively use eslint.formatEach() (see Docs). 
		.pipe(eslint.format())
		// To have the process exit with an error code (1) on 
		// lint error, return the stream and pipe to failAfterError last. 
		.pipe(eslint.failAfterError());
});

gulp.task('styles',function(){
	gulp.src('sass/**/*.scss')
		.pipe(sass())
		.pipe(autoprefixer( { browsers: ['last 2 versions']} ))
		.pipe(gulp.dest('dist/css'));
});


browserSync.stream();