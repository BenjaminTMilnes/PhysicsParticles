var application = angular.module("PhysicsParticles", ["ngRoute", "ngSanitize"]);

application.config(function ($routeProvider) {
    $routeProvider
        .when("/", { templateUrl: "table.html", controller: "TableController" })
        .when("/particle/:particleName", { templateUrl: "particle.html", controller: "ParticleController" });
});

application.directive("mathematics", function () {
    return {
        restrict: "E",
        link: function (scope, element, attributes) {
            var contentType = attributes.contentType;
            var content = attributes.content;
            if (typeof (katex) === "undefined") {
                require(["katex"], function (katex) {
                    katex.render(content, element[0]);
                });
            }
            else {
                katex.render(content, element[0]);
            }
        }
    }
});

application.directive("compile", ["$compile", function ($compile) {
    return function (scope, element, attributes) {
        scope.$watch(function (scope) {
            return scope.$eval(attributes.compile);
        }, function (value) {
            element.html(value);
            $compile(element.contents())(scope);
        });
    };
}]);

class Database {
    constructor(data) {
        this._data = data;

        this._particlesObject = {}

        this._data.Particles.forEach(p => {
            this._particlesObject[p.Reference] = p;
        });
    }

    get particles() {
        return this._data.Particles;
    }

    get tableData() {
        return this._particlesObject;
    }

    getParticleWithURLReference(urlReference) {
        var ps = this.particles.filter(p => p.URLReference == urlReference);

        return (ps.length > 0) ? ps[0] : null;
    }
}

application.factory("dataService", ["$http", function ($http) {
    var dataService = {
        data: null,
        getData: function () {
            var that = this;

            if (this.data != null) {
                return new Promise(function (resolve, reject) { return resolve(that.data); });
            }

            return $http.get("particles.json").then(function (response) {
                that.data = response.data;

                return response.data;
            });
        }
    };

    return dataService;
}]);

application.directive("particle", function () {
    return {
        restrict: "E",
        templateUrl: "particle-block.html",
        scope: {
            particle: "=data"
        }
    };
});

application.controller("TableController", ["$scope", "$routeParams", "dataService", "$rootScope", function TableController($scope, $routeParams, dataService, $rootScope) {

    dataService.getData().then(function (data) {
        var database = new Database(data);

        $scope.particles = database.tableData;
    });
}]);

application.controller("ParticleController", ["$scope", "$routeParams", "dataService", "$rootScope", function ParticleController($scope, $routeParams, dataService, $rootScope) {

    dataService.getData().then(function (data) {
        var database = new Database(data);

        $scope.particle = database.getParticleWithURLReference($routeParams.particleName);
    });

}]);